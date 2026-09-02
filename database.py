import sqlite3
from datetime import datetime

db = sqlite3.connect('bookings.db')
cursor = db.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    first_name TEXT,
    booking_date TEXT,
    topic TEXT,
    event_datetime TEXT,
    reminded_24h INTEGER DEFAULT 0,
    reminded_3h INTEGER DEFAULT 0,
    timestamp TEXT
)
''')
db.commit()

def add_booking(user_id, username, first_name, booking_date, topic, event_datetime):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    INSERT INTO bookings (user_id, username, first_name, booking_date, topic, event_datetime, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, booking_date, topic, event_datetime, timestamp))
    db.commit()

def get_all_bookings():
    cursor.execute('SELECT first_name, username, booking_date, topic, timestamp FROM bookings ORDER BY id DESC')
    return cursor.fetchall()

def get_booking_by_user(user_id):
    cursor.execute('''
    SELECT id, booking_date, topic, event_datetime FROM bookings
    WHERE user_id = ? AND datetime(event_datetime) > datetime('now')
    ORDER BY id DESC LIMIT 1
    ''', (user_id,))
    return cursor.fetchone()

def delete_booking(booking_id):
    cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    db.commit()

def get_users_to_remind_24h():
    cursor.execute('''
    SELECT user_id, first_name, event_datetime, id FROM bookings
    WHERE reminded_24h = 0
    ''')
    return cursor.fetchall()

def get_users_to_remind_3h():
    cursor.execute('''
    SELECT user_id, first_name, event_datetime, id FROM bookings
    WHERE reminded_3h = 0
    ''')
    return cursor.fetchall()

def mark_reminded_24h(booking_id):
    cursor.execute('UPDATE bookings SET reminded_24h = 1 WHERE id = ?', (booking_id,))
    db.commit()

def mark_reminded_3h(booking_id):
    cursor.execute('UPDATE bookings SET reminded_3h = 1 WHERE id = ?', (booking_id,))
    db.commit()
