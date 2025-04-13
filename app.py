from flask import Flask, render_template, request, redirect, url_for
from models import add_found_item, add_lost_item, get_lost_items, get_found_items, get_matches
from db import connect

import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_lost', methods=['GET', 'POST'])
def lost():
    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        location = request.form['location']
        lost_date = request.form['lost_date']
        contact = request.form['contact']

        image = request.files.get('image')
        image_filename = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

        # Add the lost item to the database
        item_id = add_lost_item(item_name, description, location, lost_date, contact, image_filename)


        # Fetch possible matches based on the item_id
        matches = get_matches(item_id)  # You'll need to implement this function

        return render_template('matches.html', matches=matches, lost_id=item_id)


    return render_template('add_lost.html')  # If GET request, show the form to add a lost item



@app.route('/add_found', methods=['GET', 'POST'])
def found():
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        location = request.form.get('location')
        found_date = request.form.get('found_date')
        contact = request.form['contact']

        image = request.files.get('image')
        image_filename = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

        item_id = add_found_item(item_name, description, location, found_date, contact, image_filename)

        return redirect('/view_lost')

    return render_template('add_found.html')


@app.route('/view_lost')
def view_lost():
    items = get_lost_items()
    return render_template('view_lost.html', items=items)

@app.route('/view_found')
def view_found():
    items = get_found_items()
    return render_template('view_found.html', items=items)

@app.route('/claim_lost_later/<int:lost_id>', methods=['POST'])
def claim_lost_later(lost_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE Lost_Items SET status = 'Found' WHERE lost_id = %s", (lost_id,))
    conn.commit()
    conn.close()
    return redirect('/view_lost')

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/claim_lost/<int:lost_id>/<int:found_id>", methods=["POST"])
def claim_lost(lost_id, found_id):
    try:
        conn = connect()
        cursor = conn.cursor()

        # Check if the found item is already claimed
        cursor.execute("SELECT Status FROM Found_Items WHERE found_id = %s", (found_id,))
        found_status = cursor.fetchone()
        if not found_status:
            return redirect(url_for("home"))
        if found_status[0] == "Claimed":
            return redirect(url_for("home"))

        # Check if the lost item exists
        cursor.execute("SELECT Status FROM Lost_Items WHERE lost_id = %s", (lost_id,))
        lost_status = cursor.fetchone()
        if not lost_status:
            return redirect(url_for("home"))

        # ✅ Update Found_Items table
        cursor.execute("UPDATE Found_Items SET Status = 'Claimed' WHERE found_id = %s", (found_id,))

        # ✅ Update Lost_Items table
        cursor.execute("UPDATE Lost_Items SET Status = 'Resolved' WHERE lost_id = %s", (lost_id,))

        conn.commit()

    except Exception as e:
        print("Error during claim process:", e)

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
