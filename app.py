from flask import Flask, render_template, request, redirect
from models import add_found_item, add_lost_item, get_lost_items, get_found_items, claim_item, get_matches
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
        date = request.form['lost_date']

        image = request.files.get('image')
        image_filename = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

        item_id = add_lost_item(item_name, description, location, date, image_filename)
        return redirect(f'/matches/{item_id}')
    return render_template('add_lost.html')

@app.route('/add_found', methods=['GET', 'POST'])
def found():
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        location = request.form.get('location')
        found_date = request.form.get('found_date')

        image = request.files.get('image')
        image_filename = None

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

        add_found_item(item_name, description, location, found_date, image_filename)
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

@app.route('/claim_lost/<int:lost_id>', methods=['POST'])
def claim_lost(lost_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE Lost_Items SET status = 'Found' WHERE lost_id = %s", (lost_id,))
    conn.commit()
    conn.close()
    return redirect('/view_lost')

@app.route('/matches/<int:item_id>')
def show_matches(item_id):
    matches = get_matches(item_id)
    return render_template('matches.html', matches=matches)



if __name__ == '__main__':
    app.run(debug=True)
