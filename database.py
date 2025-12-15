# database.py
# --- FINAL VERSION (U4 - ADMIN FUNCTIONS ADDED) ---

import sqlite3
import hashlib
import datetime
import os

DB_FILE = "village_service.db"

# ---------- Connection ----------
def get_connection():
    return sqlite3.connect(DB_FILE)

# ---------- Password Hashing ----------
def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()

# ---------- Database Setup ----------
def connect_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Customers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        password TEXT NOT NULL,
        address TEXT,
        created_at TEXT
    )
    """)

    # Workers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        password TEXT NOT NULL,
        skill TEXT,
        experience INTEGER,
        price_per_hour REAL,
        availability TEXT,
        photo TEXT,
        rating REAL DEFAULT 0,
        address TEXT,
        created_at TEXT
    )
    """)

    # Bookings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        worker_id INTEGER,
        service_date TEXT,
        status TEXT,
        address TEXT,
        notes TEXT,
        created_at TEXT,
        FOREIGN KEY(customer_id) REFERENCES users(user_id) ON DELETE SET NULL,
        FOREIGN KEY(worker_id) REFERENCES workers(worker_id) ON DELETE SET NULL
    )
    """)

    # Reviews table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER UNIQUE,
        customer_id INTEGER,
        worker_id INTEGER,
        rating INTEGER,
        review_text TEXT,
        created_at TEXT,
        FOREIGN KEY(booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
        FOREIGN KEY(customer_id) REFERENCES users(user_id) ON DELETE SET NULL,
        FOREIGN KEY(worker_id) REFERENCES workers(worker_id) ON DELETE SET NULL
    )
    """)
    
    # Chat Messages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER,
        sender_id INTEGER,
        sender_type TEXT, -- 'customer' or 'worker'
        message_text TEXT,
        timestamp TEXT,
        FOREIGN KEY(booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE
    )
    """)

    # Admin table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)

    # Default Admin
    cursor.execute("""
        INSERT OR IGNORE INTO admin (username, password)
        VALUES (?, ?)
    """, ("admin", hash_password("admin123")))

    conn.commit()
    conn.close()

# ------------------------------------------------
#                CUSTOMER FUNCTIONS
# ------------------------------------------------
def register_customer(name, email, phone, plain_password, address=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed_pw = hash_password(plain_password)
        created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO users (name, email, phone, password, address, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, phone, hashed_pw, address, created))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Email already exists!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def verify_customer(email_or_phone, plain_password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(plain_password)
    cursor.execute("""
        SELECT user_id, name, email, phone, address
        FROM users
        WHERE (email = ? OR phone = ?) AND password = ?
    """, (email_or_phone, email_or_phone, hashed_pw))
    row = cursor.fetchone()
    conn.close()
    if row:
        return True, {"user_id": row[0], "name": row[1], "email": row[2], "phone": row[3], "address": row[4]}
    return False, None

def get_customer_details(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, name, email, phone, address
        FROM users
        WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"user_id": row[0], "name": row[1], "email": row[2], "phone": row[3], "address": row[4]}
    return None

# ------------------------------------------------
#                WORKER FUNCTIONS
# ------------------------------------------------
def register_worker(name, email, phone, plain_password, skill, exp, price_per_hour,
                    availability, address, photo_path):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        hashed_pw = hash_password(plain_password)
        created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO workers
            (name, email, phone, password, skill, experience, price_per_hour,
             availability, address, photo, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, hashed_pw, skill, exp, price_per_hour,
              availability, address, photo_path, created))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Worker email already exists!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def verify_worker(email_or_phone, plain_password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(plain_password)
    cursor.execute("""
        SELECT worker_id, name, email, phone, skill, availability, price_per_hour
        FROM workers
        WHERE (email = ? OR phone = ?) AND password = ?
    """, (email_or_phone, email_or_phone, hashed_pw))
    row = cursor.fetchone()
    conn.close()
    if row:
        return True, {"worker_id": row[0], "name": row[1], "email": row[2], "phone": row[3], "skill": row[4], "availability": row[5], "price_per_hour": row[6]}
    return False, None

# ------------------------------------------------
#                PROFILE FUNCTIONS
# ------------------------------------------------
def get_worker_profile(worker_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT worker_id, name, email, phone, skill, experience,
               price_per_hour, availability, address, photo, rating
        FROM workers WHERE worker_id = ?
    """, (worker_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_worker_profile(worker_id, name, phone, skill, experience,
                          price_per_hour, availability, address, photo):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE workers
            SET name=?, phone=?, skill=?, experience=?, price_per_hour=?,
                availability=?, address=?, photo=?
            WHERE worker_id=?
        """, (name, phone, skill, experience, price_per_hour,
              availability, address, photo, worker_id))
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# ------------------------------------------------
#                 SEARCH FUNCTIONS
# ------------------------------------------------
def get_worker_list_for_search():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT worker_id, name, skill, price_per_hour, availability, photo, rating, address
        FROM workers ORDER BY worker_id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_workers(keyword="", skill=None, min_price=None, max_price=None, availability=None):
    conn = get_connection()
    cursor = conn.cursor()
    base = "SELECT worker_id, name, skill, price_per_hour, availability, photo, rating, address FROM workers WHERE 1=1"
    params = []
    if keyword:
        base += " AND (name LIKE ? OR skill LIKE ? OR address LIKE ?)"
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw])
    if skill and skill != "All":
        base += " AND skill = ?"
        params.append(skill)
    if availability and availability != "All":
        base += " AND availability = ?"
        params.append(availability)
    if min_price is not None:
        base += " AND price_per_hour >= ?"
        params.append(min_price)
    if max_price is not None:
        base += " AND price_per_hour <= ?"
        params.append(max_price)
    base += " ORDER BY price_per_hour ASC"
    cursor.execute(base, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ------------------------------------------------
#                  BOOKING SYSTEM
# ------------------------------------------------
def create_booking(customer_id, worker_id, service_date, address, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO bookings (customer_id, worker_id, service_date, status, address, notes, created_at)
            VALUES (?, ?, ?, 'Pending', ?, ?, ?)
        """, (customer_id, worker_id, service_date, address, notes, created))
        conn.commit()
        return True, cursor.lastrowid
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_bookings_by_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.booking_id, b.worker_id, w.name, w.skill, b.service_date, b.status, b.address, b.notes
        FROM bookings b
        LEFT JOIN workers w ON b.worker_id = w.worker_id
        WHERE b.customer_id=?
        ORDER BY b.booking_id DESC
    """, (customer_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_bookings_by_worker(worker_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.booking_id, b.customer_id, u.name, u.phone, b.service_date, b.status, b.address, b.notes
        FROM bookings b
        LEFT JOIN users u ON b.customer_id = u.user_id
        WHERE b.worker_id=?
        ORDER BY b.booking_id DESC
    """, (worker_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_booking_status(booking_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE bookings SET status=? WHERE booking_id=?", (status, booking_id))
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# ------------------------------------------------
#                  RATING SYSTEM (U2)
# ------------------------------------------------
def _update_worker_average_rating(worker_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT AVG(rating) FROM reviews WHERE worker_id=?", (worker_id,))
        avg_rating = cursor.fetchone()[0]
        if avg_rating is None:
            avg_rating = 0
        cursor.execute("UPDATE workers SET rating=? WHERE worker_id=?", (avg_rating, worker_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating rating: {e}")
    finally:
        conn.close()

def add_review(booking_id, customer_id, worker_id, rating, review_text):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO reviews (booking_id, customer_id, worker_id, rating, review_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (booking_id, customer_id, worker_id, rating, review_text, created))
        conn.commit()
        _update_worker_average_rating(worker_id)
        return True, None
    except sqlite3.IntegrityError:
        return False, "A review for this booking already exists."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def check_if_reviewed(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM reviews WHERE booking_id=?", (booking_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

# ------------------------------------------------
#                  CHAT SYSTEM (U3)
# ------------------------------------------------
def send_message(booking_id, sender_id, sender_type, message):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO messages (booking_id, sender_id, sender_type, message_text, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (booking_id, sender_id, sender_type, message, ts))
        conn.commit()
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_messages(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender_id, sender_type, message_text, timestamp
        FROM messages
        WHERE booking_id = ?
        ORDER BY timestamp ASC
    """, (booking_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# ------------------------------------------------
#                  ADMIN FUNCTIONS (U4)
# ------------------------------------------------
def get_app_stats():
    """Fetches count of users, workers, and bookings."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM workers")
        worker_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM bookings")
        booking_count = cursor.fetchone()[0]
        return {"users": user_count, "workers": worker_count, "bookings": booking_count}
    except Exception as e:
        return {"users": 0, "workers": 0, "bookings": 0}
    finally:
        conn.close()

def get_all_users():
    """Fetches all customer details for admin table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, phone, address FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_user(user_id):
    """Deletes a user and all their related data (bookings, reviews)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = ON;")
        # Deleting user will set related fields in bookings/reviews to NULL (due to ON DELETE SET NULL)
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        # We also delete their messages
        cursor.execute("DELETE FROM messages WHERE sender_id = ? AND sender_type = 'customer'", (user_id,))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_all_workers():
    """Fetches all worker details for admin table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT worker_id, name, skill, phone, rating, availability FROM workers")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_worker(worker_id):
    """Deletes a worker and all their related data."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("DELETE FROM workers WHERE worker_id = ?", (worker_id,))
        cursor.execute("DELETE FROM messages WHERE sender_id = ? AND sender_type = 'worker'", (worker_id,))
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

def get_all_bookings():
    """Fetches all booking details for admin table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT booking_id, customer_id, worker_id, service_date, status, address FROM bookings")
    rows = cursor.fetchall()
    conn.close()
    return rows


# Auto init
if __name__ == "__main__":
    connect_db()
    print("Database initialized:", os.path.exists(DB_FILE))