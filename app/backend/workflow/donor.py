import os
import uuid
import pandas as pd

DONATION_FILE = "app/backend/data/donations.csv"

def submit_donation(donor_name, contact, location, food_desc, mood=None, food_img=None):
    """Save donor submission with optional image and sentiment/mood."""

    try:
        os.makedirs(os.path.dirname(DONATION_FILE), exist_ok=True)

        donation_id = str(uuid.uuid4())[:8]
        img_path = None

        # Save uploaded image (if any)
        if food_img is not None:
            img_dir = "app/backend/data/donation_images"
            os.makedirs(img_dir, exist_ok=True)
            img_path = os.path.join(img_dir, f"{donation_id}.jpg")
            with open(img_path, "wb") as f:
                f.write(food_img.read())

        record = {
            "donation_id": donation_id,
            "donor_name": donor_name,
            "contact": contact,
            "location": location,
            "food_desc": food_desc,
            "mood": mood if mood else "NEUTRAL",
            "image_path": img_path,
            "status": "Available"
        }

        # Append to existing CSV or create new
        if os.path.exists(DONATION_FILE):
            df = pd.read_csv(DONATION_FILE)
            df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        else:
            df = pd.DataFrame([record])

        df.to_csv(DONATION_FILE, index=False)

        return {"status": "success", "donation_id": donation_id}

    except Exception as e:
        return {"status": "error", "message": str(e)}
