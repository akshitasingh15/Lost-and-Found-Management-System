from db import connect
from fuzzywuzzy import fuzz
from datetime import datetime
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
            INSERT INTO Found_Items (item_name, description, found_location, found_date, status, image_path)
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

def get_matches(item_id, threshold=30):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT item_name, description, lost_location, lost_date FROM Lost_Items WHERE lost_id = %s", (item_id,))
    lost_item = cursor.fetchone()

    if not lost_item:
        conn.close()
        return []

    lost_name, lost_description, lost_location, lost_date = lost_item

    cursor.execute("SELECT * FROM Found_Items WHERE Status = 'Pending'")
    found_items = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    conn.close()

    scored_matches = []
    for item in found_items:
        item_dict = dict(zip(columns, item))

        print("Lost Date:", lost_date)
        print("Found Date:", item_dict['found_date'])

        if item_dict['found_date'] < lost_date:
            print("Skipping because found before lost")
            continue


        name_score = fuzz.partial_ratio(lost_name.lower(), item_dict['item_name'].lower())
        desc_score = fuzz.partial_ratio(lost_description.lower(), item_dict['description'].lower())
        location_score = fuzz.partial_ratio(lost_location.lower(), item_dict['found_location'].lower())
        date_score = fuzz.partial_ratio(str(lost_date), str(item_dict['found_date']))

        # Weighted average: prioritize item_name
        avg_score = (
            name_score * 0.4 +
            desc_score * 0.3 +
            location_score * 0.2 +
            date_score * 0.1
        )

        if avg_score >= threshold:
            item_dict['match_score'] = round(avg_score, 2)
            scored_matches.append(item_dict)

    scored_matches.sort(key=itemgetter('match_score'), reverse=True)
    return scored_matches
