import pandas as pd
import os

DONATION_FILE = "app/backend/data/donations.csv"

def view_and_claim_donations():
    """Return all unclaimed donations for NGOs to view."""
    if not os.path.exists(DONATION_FILE):
        return pd.DataFrame()

    df = pd.read_csv(DONATION_FILE)
    available = df[df["status"] == "Available"].copy()
    return available


def claim_donation(donation_id, ngo_name):
    """Mark a donation as claimed by an NGO."""
    if not os.path.exists(DONATION_FILE):
        return {"status": "error", "message": "Donation file not found."}

    df = pd.read_csv(DONATION_FILE)

    if donation_id not in df["donation_id"].values:
        return {"status": "error", "message": "Invalid donation ID."}

    df.loc[df["donation_id"] == donation_id, "status"] = f"Claimed by {ngo_name}"
    df.to_csv(DONATION_FILE, index=False)

    return {"status": "success", "message": f"Donation {donation_id} claimed by {ngo_name}"}
