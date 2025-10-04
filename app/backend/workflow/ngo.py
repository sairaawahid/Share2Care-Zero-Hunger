import pandas as pd
import os

DONATION_FILE = "app/backend/data/donations.csv"

def view_and_claim_donations():
    """Load available donations for NGOs to view."""
    if not os.path.exists(DONATION_FILE):
        return pd.DataFrame()

    df = pd.read_csv(DONATION_FILE)
    available = df[df["status"] == "Available"].copy()
    return available
