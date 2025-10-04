# app/backend/data/init_donations_csv.py
import pandas as pd
import os

os.makedirs("app/backend/data", exist_ok=True)
file = "app/backend/data/donations.csv"

cols = [
    "donation_id", "donor_name", "contact", "location",
    "food_desc", "mood", "image_path", "status"
]

if not os.path.exists(file):
    pd.DataFrame(columns=cols).to_csv(file, index=False)
    print("✅ donations.csv initialized.")
else:
    print("✅ donations.csv already exists.")
