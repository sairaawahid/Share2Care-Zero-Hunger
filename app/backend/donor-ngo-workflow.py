import os
import sqlite3
from datetime import datetime
from app.backend.models.sentiment import analyze_sentiment
from app.backend.models.image_tagging import tag_food_image

DB_PATH = os.path.join(os.path.dirname(__file__), "donations.db")


def init_db():
    """Initialize donations table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_name TEXT,
            donor_contact TEXT,
            food_description TEXT,
            quantity TEXT,
            location TEXT,
            image_path TEXT,
            tags TEXT,
            note TEXT,
            mood TEXT,
            status TEXT DEFAULT 'Open',
            ngo_name TEXT,
            ngo_contact TEXT,
            claim_time TEXT,
            delivered_time TEXT
        )
    """)
    conn.commit()
    conn.close()


def submit_donation(donor_name, donor_contact, food_description, quantity, location, note=None, image_path=None):
    """Handle donor submission, run image tagging & sentiment if applicable."""
    tags = None
    mood = None

    if image_path and os.path.exists(image_path):
        try:
            tags = ", ".join(tag_food_image(image_path))
        except Exception as e:
            print(f"[WARN] Image tagging failed: {e}")

    if note:
        try:
            mood = analyze_sentiment(note)
        except Exception as e:
            print(f"[WARN] Sentiment analysis failed: {e}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO donations (donor_name, donor_contact, food_description, quantity, location, image_path, tags, note, mood, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (donor_name, donor_contact, food_description, quantity, location, image_path, tags, note, mood, 'Open'))
    conn.commit()
    donation_id = c.lastrowid
    conn.close()

    return {
        "donation_id": donation_id,
        "tags": tags,
        "mood": mood,
        "message": f"Thanks {donor_name}! Your donation has been recorded."
    }


def list_donations(status="Open"):
    """List all donations by status."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM donations WHERE status=?", (status,))
    rows = c.fetchall()
    conn.close()

    cols = ["id", "donor_name", "donor_contact", "food_description", "quantity", "location",
            "image_path", "tags", "note", "mood", "status", "ngo_name", "ngo_contact",
            "claim_time", "delivered_time"]
    return [dict(zip(cols, row)) for row in rows]


def claim_donation(donation_id, ngo_name, ngo_contact):
    """NGO claims a donation."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE donations SET status=?, ngo_name=?, ngo_contact=?, claim_time=? WHERE id=?
    """, ('Claimed', ngo_name, ngo_contact, datetime.now().isoformat(), donation_id))
    conn.commit()
    conn.close()
    return {"message": f"Donation #{donation_id} claimed by {ngo_name}."}


def confirm_delivery(donation_id):
    """NGO confirms food delivered; trigger donor feedback."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE donations SET status=?, delivered_time=? WHERE id=?
    """, ('Delivered', datetime.now().isoformat(), donation_id))
    conn.commit()
    conn.close()

    # Generate feedback message
    feedback_msg = generate_feedback_message(donation_id)
    return {"message": feedback_msg}


def generate_feedback_message(donation_id):
    """Generate donor-facing feedback message based on mood and sentiment."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT donor_name, mood FROM donations WHERE id=?", (donation_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "Donation not found."

    donor_name, mood = row
    if mood == "POSITIVE":
        return f"Thank you, {donor_name}! Your kind act brightened someone's day 🌻"
    elif mood == "NEGATIVE":
        return f"{donor_name}, your generosity brings hope even in tough times 💪"
    else:
        return f"Donation completed successfully. You made a real difference today 🌍"


# Initialize database on import
init_db()
