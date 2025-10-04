import os
import uuid
import pandas as pd

DONATION_FILE = "app/backend/data/donations.csv"

def submit_donation(donor_name, food_type, quantity, location, food_img=None):
    """Save donor submission to CSV with optional image path."""
    try:
        os.makedirs(os.path.dirname(DONATION_FILE), exist_ok=True)

        donation_id = str(uuid.uuid4())[:8]
        img_path = None

        if food_img is not None:
            img_dir = "app/backend/data/donation_images"
            os.makedirs(img_dir, exist_ok=True)
            img_path = os.path.join(img_dir, f"{donation_id}.jpg")
            with open(img_path, "wb") as f:
                f.write(food_img.read())

        record = {
            "donation_id": donation_id,
            "donor_name": donor_name,
            "food_type": food_type,
            "quantity": quantity,
            "location": location,
            "image_path": img_path,
            "status": "Available"
        }

        if os.path.exists(DONATION_FILE):
            df = pd.read_csv(DONATION_FILE)
            df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        else:
            df = pd.DataFrame([record])

        df.to_csv(DONATION_FILE, index=False)
        return {"status": "success", "donation_id": donation_id}

    except Exception as e:
        return {"status": "error", "message": str(e)}
