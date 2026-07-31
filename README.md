# EquipKisan 🚜

## Farm Equipment Sharing Platform

EquipKisan is a web-based platform that helps farmers find, rent, and share agricultural equipment efficiently. The platform connects equipment owners with farmers who need machinery for farming activities such as ploughing, sowing, spraying, and harvesting.

---

## Problem Statement

Many farmers cannot afford expensive agricultural machinery for occasional use. At the same time, many equipment owners have idle machinery that remains unused for long periods.

EquipKisan solves this problem by creating a sharing platform where farmers can search and book available equipment nearby.

---

## Features

### User Registration & Login

* Farmer registration
* Secure login system
* User authentication

### Equipment Recommendation

Based on farming activity:

* Ploughing → Tractor
* Sowing → Seed Drill
* Spraying → Power Sprayer
* Harvesting → Harvester

### Equipment Search

Farmers can search available equipment by:

* District
* Equipment Type

### Equipment Booking

* View available equipment owners
* Check rent details
* Select payment method
* Book equipment instantly

### Email Notifications

* Registration confirmation email
* Booking confirmation email
* SMTP-based email integration

### Database Management

* User information storage
* Equipment details storage
* Booking records management

### Equipment Search & Filters

* Free-text search across equipment, owner, and district
* Filter by equipment type (category), district, and availability
* Sort results by rent (low/high) or name
* Dedicated "Browse Equipment" page with 500+ live listings

### Booking History

* Each user gets a personal "My Bookings" page
* View past reservations: equipment, owner, district, rent, payment method, and booking date

---

## Technology Stack

### Frontend

* HTML5
* CSS3
* Jinja2 Templates

### Backend

* Python
* Flask Framework

### Database

* SQLite

### Email Service

* SMTP
* Gmail App Password Integration

---

## Project Structure

```text
EquipKisan/
│
├── app.py
├── database.db
├── .env
├── requirements.txt
├── Procfile
├── runtime.txt
├── render.yaml
│
├── templates/
│   ├── _nav.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── browse.html
│   ├── booking.html
│   ├── my-bookings.html
│   └── success.html
│
└── static/
    └── style.css
```

> Note: `database.db` is auto-created and seeded on first run, so you never have to
> run `create_db.py` / `load_data.py` manually.

---

## Installation

### Clone Project

```bash
git clone <repository-url>
cd EquipKisan
```

### Install Dependencies

```bash
pip install flask
pip install python-dotenv
```

### Configure Email

Create a `.env` file:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=yourgmail@gmail.com
SMTP_PASS=your_app_password
FROM_EMAIL=yourgmail@gmail.com
```

### Run Application

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

---

## Deployment (Render — Live Access)

The project is configured for one-click deployment on [Render](https://render.com) (free tier).
The database is created and seeded automatically on first start, so no extra steps are needed.

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "EquipKisan: farm equipment sharing platform"
git branch -M main
git remote add origin https://github.com/<your-username>/EquipKisan.git
git push -u origin main
```

### Step 2: Create the service on Render

1. Log in to [dashboard.render.com](https://dashboard.render.com)
2. Click **New +** → **Blueprint** (uses `render.yaml`) — or **New +** → **Web Service** and pick your repo
3. If using **Web Service** (not Blueprint):
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free
   - Add an environment variable `SECRET_KEY` with a random value
4. Click **Deploy** and wait ~3 minutes

### Step 3: Live URL

Render gives you a public URL like `https://equipkisan.onrender.com` — share that with anyone.

> ⚠️ **Note:** On the free plan, the SQLite database lives on an ephemeral disk and resets on
> each new deploy. User accounts and bookings created in-between deploys are cleared. For a
> permanent database, upgrade to Render Postgres or switch `DB_PATH` to a managed database.

---

## Future Enhancements

* GPS-based equipment search
* AI-powered equipment recommendation
* Real-time equipment availability tracking
* Online payment gateway integration
* Farmer rating and review system
* Mobile application support
* Predictive demand forecasting

---

## Impact

* Reduces equipment ownership costs
* Improves machinery utilization
* Supports small and marginal farmers
* Encourages agricultural resource sharing
* Promotes sustainable farming practices

---

## Team

Developed as a Hackathon Project under the theme of Smart Agriculture and Resource Sharing.

---

## License

This project is developed for educational and hackathon purposes.
