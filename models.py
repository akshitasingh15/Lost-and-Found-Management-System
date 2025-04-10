from db import connect
from fuzzywuzzy import fuzz
from operator import itemgetter

def add_lost_item(item_name, description, location, date, image_path=None):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Lost_Items (item_name, description, lost_location, lost_date, status, image_path)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (item_name, description, location, date, 'Pending', image_path))
    item_id = cursor.lastrowid  # ✅ gets the auto-incremented ID
    conn.commit()
    conn.close()
    return item_id

def add_found_item(item_name, description, location, date, image_path=None):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
            INSERT INTO Found_items (item_name, description, found_location, found_date, status, image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (item_name, description, location, date, 'Pending', image_path))
    conn.commit()
    conn.close()

def get_lost_items():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Lost_Items where Status='Pending'")
    items = cursor.fetchall()
    conn.close()
    return items

def get_found_items():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Found_Items where Status='Pending'")
    items = cursor.fetchall()
    conn.close()
    return items

def claim_item(table, item_id):
    conn = connect()
    cursor = conn.cursor()

    id_column = "lost_id" if table == "Lost_Items" else "found_id"
    query = f"UPDATE {table} SET status = 'Claimed' WHERE {id_column} = %s"

    cursor.execute(query, (item_id,))
    conn.commit()
    conn.close()

def get_matches(item_id, threshold=50):
    conn = connect()
    cursor = conn.cursor()

    # Get the lost item details
    cursor.execute("SELECT item_name, description FROM Lost_Items WHERE lost_id = %s", (item_id,))
    lost_item = cursor.fetchone()

    if not lost_item:
        conn.close()
        return []

    lost_name, lost_description = lost_item

    # Get all pending found items
    cursor.execute("SELECT * FROM Found_Items WHERE Status = 'Pending'")
    found_items = cursor.fetchall()

    # Get column names to reconstruct dictionaries (optional but clean)
    columns = [desc[0] for desc in cursor.description]

    conn.close()

    # Fuzzy match found items
    scored_matches = []
    for item in found_items:
        item_dict = dict(zip(columns, item))

        name_score = fuzz.partial_ratio(lost_name.lower(), item_dict['item_name'].lower())
        desc_score = fuzz.partial_ratio(lost_description.lower(), item_dict['description'].lower())

        avg_score = (name_score + desc_score) / 2

        if avg_score >= threshold:
            item_dict['match_score'] = avg_score
            scored_matches.append(item_dict)

    # Sort matches by match score descending
    scored_matches.sort(key=itemgetter('match_score'), reverse=True)

    return scored_matches



