from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import csv
import secrets
import smtplib
from email.message import EmailMessage
import logging
import ssl
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
CSV_PATH = os.path.join(BASE_DIR, "Farm_Equipment_Sharing_Platform_Dataset.csv")

load_dotenv(os.path.join(BASE_DIR, ".env"))
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

logging.basicConfig(level=logging.INFO)

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", SMTP_USER)


# ─── Database bootstrap ─────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def seed_equipment(c):
    if not os.path.exists(CSV_PATH):
        return 0
    count = 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            c.execute(
                "INSERT OR IGNORE INTO equipment"
                "(equipment_no, equipment_name, owner_name, availability, district, phone, rent)"
                " VALUES(?,?,?,?,?,?,?)",
                (
                    (row.get("Equipment No") or "").strip(),
                    (row.get("Equipment Name") or "").strip(),
                    (row.get("Owner Name") or "").strip(),
                    (row.get("Availability") or "Available").strip(),
                    (row.get("District") or "").strip(),
                    (row.get("Phone Number") or "").strip(),
                    int(float((row.get("Rent Per Hour (INR)") or 0) or 0)),
                ),
            )
            count += 1
    return count


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS equipment(
        equipment_no TEXT,
        equipment_name TEXT,
        owner_name TEXT,
        availability TEXT,
        district TEXT,
        phone TEXT,
        rent INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_email TEXT,
        equipment_name TEXT,
        owner_name TEXT,
        district TEXT,
        phone TEXT,
        rent INTEGER,
        payment_method TEXT,
        booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    c.execute("SELECT COUNT(*) FROM equipment")
    if c.fetchone()[0] == 0:
        seed_equipment(c)
    conn.commit()
    conn.close()


def send_email(to_email, subject, body):
    if not SMTP_HOST or not SMTP_USER:
        return False
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        if SMTP_PORT == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
        return True
    except Exception as e:
        return False


@app.route('/')
def home():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        pw = request.form.get('password', '').strip()
        if not name or not email or not pw:
            flash('All fields are required.')
            return render_template('register.html')
        if len(pw) < 4:
            flash('Password must be at least 4 characters.')
            return render_template('register.html')
        h = generate_password_hash(pw)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users(name,email,password) VALUES(?,?,?)', (name,email,h))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash('Email already registered. Please log in.')
            return render_template('register.html')
        conn.close()
        send_email(email, 'Welcome', 'Registered successfully.')
        flash('Registered successfully. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    area = session.pop('rec_area', '')
    crop = session.pop('rec_crop', '')
    work = session.pop('rec_work', '')
    equipment_list = session.pop('rec_equipment_list', None)
    available_list = session.pop('rec_available_list', None)
    return render_template('dashboard.html', area=area, crop=crop, work=work,
                           equipment_list=equipment_list, available_list=available_list)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        pw = request.form.get('password', '').strip()
        if not email or not pw:
            flash('Please enter email and password.')
            return render_template('login.html')
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email=?', (email,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[3], pw):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.')
    return render_template('login.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('login.html'), 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/recommend', methods=['POST'])
def recommend():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    area = request.form.get('area', '').strip()
    crop = request.form.get('crop', '').strip()
    work = request.form.get('work', '').strip()
    if not work:
        flash('Please select a field work type.')
        return redirect(url_for('dashboard'))

    eq_map = {
        'Ploughing': ['Tractor', 'Cultivator', 'Disc Harrow', 'Rotavator', 'Laser Land Leveler'],
        'Sowing': ['Seed Drill', 'Paddy Transplanter'],
        'Spraying': ['Power Sprayer', 'Sprayer (Battery Powered)'],
        'Harvesting': ['Combine Harvester', 'Thresher', 'Balers'],
        'Weeding': ['Power Weeder', 'Cultivator'],
        'Tilling': ['Power Tiller', 'Rotavator'],
        'Leveling': ['Laser Land Leveler'],
        'Chaff Cutting': ['Chaff Cutter'],
    }
    eq_list = eq_map.get(work, ['Tractor'])

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    available_list = []
    for eq in eq_list:
        c.execute("SELECT COUNT(*) FROM equipment WHERE equipment_name=? AND availability='Available'", (eq,))
        if c.fetchone()[0] > 0:
            available_list.append(eq)
    conn.close()
    session['rec_area'] = area
    session['rec_crop'] = crop
    session['rec_work'] = work
    session['rec_equipment_list'] = eq_list
    session['rec_available_list'] = available_list
    return redirect(url_for('dashboard'))

@app.route('/search', methods=['POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    dist = request.form.get('district', '').strip()
    eq = request.form.get('equipment', '').strip()
    if not dist or not eq:
        flash('Please enter district and equipment.')
        return redirect(url_for('dashboard'))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM equipment WHERE district=? AND availability='Available' AND equipment_name=?", (dist, eq))
    data = c.fetchall()
    conn.close()
    return render_template('booking.html', data=data)

@app.route('/browse')
def browse():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    q = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    district = request.args.get('district', '').strip()
    availability = request.args.get('availability', '').strip()
    sort = request.args.get('sort', 'rent_asc').strip()

    conditions = []
    params = []
    if q:
        conditions.append("(equipment_name LIKE ? OR owner_name LIKE ? OR district LIKE ?)")
        params += [f"%{q}%", f"%{q}%", f"%{q}%"]
    if category:
        conditions.append("equipment_name = ?")
        params.append(category)
    if district:
        conditions.append("district = ?")
        params.append(district)
    if availability:
        conditions.append("availability = ?")
        params.append(availability)

    order_by = "rent ASC"
    if sort == 'rent_desc':
        order_by = "rent DESC"
    elif sort == 'name':
        order_by = "equipment_name ASC, rent ASC"

    sql = "SELECT * FROM equipment"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY " + order_by

    conn = get_db()
    rows = conn.execute(sql, params).fetchall()
    categories = [r[0] for r in conn.execute(
        "SELECT DISTINCT equipment_name FROM equipment ORDER BY equipment_name")]
    districts = [r[0] for r in conn.execute(
        "SELECT DISTINCT district FROM equipment ORDER BY district")]
    conn.close()

    return render_template('browse.html', rows=rows, categories=categories, districts=districts,
                           q=q, category=category, district=district,
                           availability=availability, sort=sort, total=len(rows))

@app.route('/book/<equipment_no>')
def book_form(equipment_no):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    row = conn.execute("SELECT * FROM equipment WHERE equipment_no=? AND availability='Available'",
                       (equipment_no,)).fetchone()
    conn.close()
    if not row:
        flash('This equipment is not available for booking.')
        return redirect(url_for('browse'))
    return render_template('booking.html', data=[row], single=True)

@app.route('/my-bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    bookings = conn.execute(
        "SELECT * FROM bookings WHERE user_id=? ORDER BY booking_date DESC",
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('my-bookings.html', bookings=bookings)

@app.route('/book', methods=['POST'])
def book():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    owner = request.form.get('owner', '').strip()
    payment = request.form.get('payment', '').strip()
    eq = request.form.get('equipment', '').strip()
    eq_no = request.form.get('equipment_no', '').strip()
    district = request.form.get('district', '').strip()
    phone = request.form.get('phone', '').strip()
    rent = request.form.get('rent', '').strip()
    user_email = request.form.get('user_email', '').strip()
    if not owner or not payment or not eq:
        flash('Booking information is incomplete.')
        return redirect(url_for('browse'))
    uid = session.get('user_id')
    ue = user_email or session.get('user_email', '')
    rent_int = int(rent) if rent.isdigit() else None
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO bookings(user_id, user_email, equipment_name, owner_name,
                 payment_method, district, phone, rent)
                 VALUES(?,?,?,?,?,?,?,?)''', (uid, ue, eq, owner, payment, district, phone, rent_int))
    if eq_no:
        c.execute("UPDATE equipment SET availability='Rented Out' WHERE equipment_no=? AND owner_name=?", (eq_no, owner))
    conn.commit()
    conn.close()
    if ue:
        send_email(ue, 'Booking Confirmed', f'Equipment: {eq}\nOwner: {owner}\nPayment: {payment}')
    flash('Booking confirmed!')
    return render_template('success.html', owner=owner, payment=payment, equipment=eq)


init_db()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=debug_mode)
