import sys
import os

# Ensure repo root is always in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from datetime import datetime
import json
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from requests.exceptions import RequestException

from app.backend.config import (
    MERGED_SEVERITY_GEOJSON,
    IPC_SEVERITY_GEOJSON,
    WFP_FOOD_PRICES,
)
from app.backend.data_loader import load_wfp_prices
from app.backend.models.price_forecast import forecast_prices
from app.backend.models.image_tagging import tag_food_image
import PIL.Image as Image
from app.backend.models.sentiment import analyze_sentiment

# --- Donor–NGO Workflow Imports (kept for reference) ---
# we will call backend APIs (no mock fallback). If you still want to use local helper functions,
# they remain in this file but are not used when API is configured.
try:
    from app.backend.workflow.donor import submit_donation as local_submit_donation  # optional local import
    from app.backend.workflow.ngo import view_and_claim_donations as local_view_donations
except Exception:
    local_submit_donation = None
    local_view_donations = None

# -----------------------------
# API CONFIG / HELPERS
# -----------------------------
# Base API URL (override with STREAMLIT_API_URL env var); expectation: endpoints are under /api
API_BASE = os.environ.get("STREAMLIT_API_URL", "http://127.0.0.1:8000/api").rstrip("/")

API_TIMEOUT = 6  # seconds

def _api_get(path: str, params: dict = None):
    url = f"{API_BASE}{path}"
    try:
        r = requests.get(url, params=params or {}, timeout=API_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except RequestException as e:
        st.error(f"API GET failed ({url}): {e}")
        raise

def _api_post(path: str, payload: dict = None, files: dict = None):
    url = f"{API_BASE}{path}"
    try:
        r = requests.post(url, json=payload, files=files or None, timeout=API_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except RequestException as e:
        st.error(f"API POST failed ({url}): {e}")
        raise

# Donations endpoints (expected)
def api_list_donations(status: str = "Open"):
    # Expect GET /donations?status=Open
    return _api_get("/donations", params={"status": status})

def api_submit_donation(donor_name, contact, location, food_desc, mood=None, image_bytes=None, image_filename=None):
    # Expect POST /donations
    payload = {
        "donor_name": donor_name,
        "donor_contact": contact,
        "food_description": food_desc,
        "quantity": "",            # optional
        "location": location,
        "note": "",
        "mood": mood or ""
    }
    # If backend supports file upload via multipart/form-data: send file in `files`
    files = None
    if image_bytes is not None and image_filename:
        files = {"image": (image_filename, image_bytes, "image/jpeg")}
        # For multipart we use requests.post(files=...) inside _api_post; but our _api_post uses json by default.
        # So do a direct requests call here:
        url = f"{API_BASE}/donations"
        try:
            r = requests.post(url, data=payload, files=files, timeout=API_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except RequestException as e:
            st.error(f"API POST failed ({url}): {e}")
            raise
    else:
        return _api_post("/donations", payload)

def api_claim_donation(donation_id: int, ngo_name: str, ngo_contact: str = ""):
    # Expect POST /donations/{id}/claim
    return _api_post(f"/donations/{donation_id}/claim", {"ngo_name": ngo_name, "ngo_contact": ngo_contact})

def api_mark_delivered(donation_id: int):
    # Expect POST /donations/{id}/deliver or similar
    return _api_post(f"/donations/{donation_id}/deliver", {"donation_id": donation_id})

def api_get_deliveries():
    # Expect GET /delivery or /deliveries
    try:
        return _api_get("/delivery")
    except Exception:
        # try alternate route
        return _api_get("/deliveries")

def api_get_analytics():
    return _api_get("/analytics/food-security")

# -----------------------------
# Local JSON helpers (kept for compatibility but NOT used if API is available)
# -----------------------------
DATA_FILE = "donations.json"

def load_donations_json_local():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    return data

def save_donations_json_local(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------------
# Geocoding cache
# -----------------------------
@st.cache_data(show_spinner=False)
def geocode_location_cached(location_text):
    """Cache geocoding results to avoid re-fetching same location."""
    geolocator = Nominatim(user_agent="ataraxai_donor_ngo_map")
    try:
        loc = geolocator.geocode(location_text, timeout=5)
        if loc:
            return (loc.latitude, loc.longitude)
    except Exception:
        return None
    return None

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Share2Care – Zero Hunger", layout="wide")

st.title("🌍 Share2Care – Zero Hunger")
st.markdown(
    """
    **Share2Care** helps visualize food insecurity in Pakistan (SDG2) using:
    - 📍 **OCHA 5W + IPC overlays** on OpenStreetMap  
    - 📈 **WFP food price monitoring & forecasts**  
    - 💚 A psychology-driven layer for pledges & mood reflection  
    """
)

# -----------------------------
# NAVIGATION
# -----------------------------
tabs = st.tabs([
    "🗺️ Map View",
    "📊 Prices & Forecast",
    "💚 Psychology Layer",
    "🍲 Food Recognition",
    "📝 Sentiment Analysis",
    "🍛 Donate Food",
    "🤝 NGO Dashboard",
    "🚚 Volunteer / Delivery"
])

# -----------------------------
# TAB 1: MAP VIEW
# -----------------------------
with tabs[0]:
    st.subheader("Food Insecurity Map of Pakistan")

    m = folium.Map(location=[30.3753, 69.3451], zoom_start=5, tiles="OpenStreetMap")

    # OCHA 5W overlay
    try:
        folium.GeoJson(
            str(MERGED_SEVERITY_GEOJSON),
            name="OCHA 5W Severity",
            tooltip=folium.GeoJsonTooltip(fields=["admin_code", "severity_score"],
                                          aliases=["Admin Code", "Severity"])
        ).add_to(m)
    except Exception as e:
        st.warning(f"⚠️ OCHA layer not available: {e}")

    # IPC overlay
    try:
        folium.GeoJson(
            str(IPC_SEVERITY_GEOJSON),
            name="IPC Food Insecurity",
            tooltip=folium.GeoJsonTooltip(fields=["severity_score"],
                                          aliases=["IPC Phase"])
        ).add_to(m)
    except Exception as e:
        st.warning(f"⚠️ IPC layer not available: {e}")

    folium.LayerControl().add_to(m)
    st_map = st_folium(m, width=1000, height=600)

# -----------------------------
# TAB 2: PRICES
# -----------------------------
with tabs[1]:
    st.subheader("Food Prices & Forecast (WFP Data)")

    try:
        df = load_wfp_prices()
        commodities = df["commodity"].unique().tolist()
        selected = st.selectbox("Choose a commodity:", commodities)

        df_sel = df[df["commodity"] == selected]

        # Plot historical trend
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df_sel["date"], df_sel["price"], label="Observed", color="blue")

        # Forecast future
        try:
            hist, fcst = forecast_prices(df_sel, periods=60)
            ax.plot(fcst["ds"], fcst["yhat"], label="Forecast", color="red")
            ax.fill_between(fcst["ds"], fcst["yhat_lower"], fcst["yhat_upper"],
                            alpha=0.2, color="red")
        except Exception as e:
            st.warning(f"⚠️ Forecast unavailable: {e}")

        ax.set_title(f"{selected} Price Trend & Forecast")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price (PKR)")
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Could not load WFP prices: {e}")

# -----------------------------
# TAB 3: PSYCHOLOGY LAYER
# -----------------------------
with tabs[2]:
    st.subheader("Psychology Layer 💚")

    st.markdown("Boost altruism, form habits, and reflect on your mood.")

    # Food pledge
    pledge = st.text_input("✍️ Make a small pledge (e.g., 'Donate 1 meal this week')")
    if pledge:
        st.success(f"Your pledge is saved: *{pledge}* 💡")

    # Habit reminder
    if st.button("🔔 Remind me to share surplus food"):
        st.info("We’ll keep nudging you each time you open this app 🚀")

    # Mood reflection (AI-assisted)
    st.markdown("### 📝 Mood Reflection (AI-assisted)")
    note = st.text_area("Write how you're feeling today:")

    if st.button("Analyze Mood"):
        if note.strip():
            res = analyze_sentiment(note)
            label, score = res["label"], res["score"]

            st.write(f"Your note: *{note}*")
            if label == "POSITIVE":
                st.success(f"😊 Positive Mood ({score:.2f}) — Keep spreading positivity! 💚")
            elif label == "NEGATIVE":
                st.warning(f"😔 Low Mood ({score:.2f}) — It's okay to feel low; helping others might lift you too 💫")
            else:
                st.info(f"😐 Neutral Mood ({score:.2f}) — Stay balanced, your efforts still matter 🌱")
        else:
            st.warning("⚠️ Please write something about your mood.")

# -----------------------------
# TAB 4: FOOD IMAGE TAGGING
# -----------------------------
with tabs[3]:
    st.subheader("🍲 Food Recognition")

    st.markdown("Upload a food photo and the app will auto-tag it using MobileNet.")

    uploaded = st.file_uploader("Upload a food image", type=["jpg","jpeg","png"])
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption="Uploaded Image", use_column_width=True)

        try:
            labels = tag_food_image(img, topk=3)

            if labels and labels[0][0] == "No food detected":
                st.warning("⚠️ No food items detected in this image. Try another photo with clearer food content.")
            elif labels and labels[0][0] == "Error":
                st.error(f"❌ Error during recognition: {labels[0][1]}")
            else:
                st.success("✅ Detected Food Items:")
                for lbl, prob in labels:
                    st.write(f"- **{lbl}** ({prob:.2f} confidence)")
        except Exception as e:
            st.error(f"❌ Could not tag image: {e}")

# -----------------------------
# TAB 5: SENTIMENT ANALYSIS
# -----------------------------
with tabs[4]:
    st.subheader("📝 Donor Note Sentiment Analysis")

    st.markdown("Write a short note about your pledge or how you feel, and AI will analyze it instantly.")

    note = st.text_area("✍️ Enter your reflection here:")

    if st.button("Analyze Sentiment"):
        if note.strip():
            res = analyze_sentiment(note)
            label = res["label"]
            score = res["score"]

            if label == "POSITIVE":
                st.success(f"😊 Positive ({score:.2f})")
            elif label == "NEGATIVE":
                st.error(f"😔 Negative ({score:.2f})")
            else:
                st.info(f"😐 Neutral/Other ({score:.2f})")
        else:
            st.warning("⚠️ Please enter some text first.")

# ----------------------------- #
# TAB 6: DONOR–NGO WORKFLOW
# ----------------------------- #
with tabs[5]:
    st.subheader("🤝 Donor–NGO Food Sharing Workflow")

    st.markdown("""
    This connects **donors** with **NGOs** through a transparent process:
    - Donors submit available food (with optional image + note)
    - NGOs view donations and claim them
    - AI provides encouragement based on donor sentiment 🌱
    """)

    mode = st.radio("Choose your role:", ["Donor", "NGO"])

    # ---------- DONOR SIDE ----------
    if mode == "Donor":
        st.markdown("### 🍱 Submit a Food Donation")

        donor_name = st.text_input("Your Name")
        contact = st.text_input("Contact Info (email / phone)")
        location = st.text_input("Pickup Location (district or coordinates)")
        food_desc = st.text_area("Describe the Food (e.g., rice, cooked meals, bread)")
        food_img = st.file_uploader("Optional: Upload Food Image", type=["jpg", "jpeg", "png"])
        note = st.text_area("Add a short note or message (optional):")

        # --- Sentiment Analysis ---
        mood = None
        if note.strip():
            res = analyze_sentiment(note)
            mood = res["label"]

        if st.button("🚀 Submit Donation"):
            if donor_name and contact and location and food_desc:
                # Prepare image bytes if provided
                image_bytes = None
                image_filename = None
                if food_img is not None:
                    image_bytes = food_img.getvalue()
                    image_filename = food_img.name

                try:
                    resp = api_submit_donation(
                        donor_name, contact, location, food_desc,
                        mood, image_bytes, image_filename
                    )
                    st.success("✅ Donation submitted successfully!")
                    st.json(resp)
                except Exception:
                    st.error("❌ Submission failed — ensure backend is running and STREAMLIT_API_URL is set correctly.")
                    # stop here
                    st.stop()

                # --- AI-Driven Encouragement ---
                if mood == "POSITIVE":
                    st.info("💚 You’re spreading hope! Keep donating regularly to make an even bigger impact.")
                elif mood == "NEGATIVE":
                    st.warning("💭 Helping others might lift your spirits too — your kindness truly matters.")
                else:
                    st.info("🌱 Thanks for your support! Every meal counts toward Zero Hunger.")
            else:
                st.error("⚠️ Please fill in all required fields.")

    # ---------- NGO SIDE ----------
    elif mode == "NGO":
        st.markdown("### 🏢 View and Claim Available Donations")

        # Fetch from API
        try:
            donations_list = api_list_donations(status="Open")
            available_df = pd.DataFrame(donations_list) if donations_list else pd.DataFrame()
        except Exception:
            st.error("❌ Could not fetch donations from backend. Please start the backend and set STREAMLIT_API_URL.")
            st.stop()

        if available_df.empty:
            st.info("No unclaimed donations available right now.")
        else:
            st.dataframe(available_df)
            # donation id may be integer or string depending on backend schema
            id_choices = available_df["id"].tolist() if "id" in available_df.columns else available_df["donation_id"].tolist()
            selected_id = st.selectbox("Select Donation ID to Claim:", id_choices)
            ngo_name = st.text_input("Enter your NGO Name")
            ngo_contact = st.text_input("Enter NGO contact (optional)")

            if st.button("Claim Selected Donation"):
                if ngo_name.strip():
                    try:
                        claim_resp = api_claim_donation(selected_id, ngo_name, ngo_contact)
                        st.success(f"✅ Donation ID {selected_id} has been claimed by {ngo_name}!")
                        st.json(claim_resp)
                    except Exception:
                        st.error("❌ Claim failed — ensure backend is running and endpoint exists.")
                else:
                    st.error("Please enter your NGO name before claiming.")

# ----------------------------- #
# TAB 7: NGO DASHBOARD
# ----------------------------- #
with tabs[6]:
    st.subheader("📊 NGO Dashboard — Donation Status Overview")

    # Fetch full donation list (all statuses)
    try:
        donations_list_all = _api_get("/donations")  # assume returns all if no status provided
        df = pd.DataFrame(donations_list_all) if donations_list_all else pd.DataFrame()
    except Exception:
        st.error("❌ Could not fetch donations from backend. Please start the backend and set STREAMLIT_API_URL.")
        st.stop()

    if df.empty:
        st.info("No donations submitted yet.")
    else:
        # --- Full data table ---
        st.dataframe(df)

        # --- Filter by status ---
        st.markdown("### 🔍 Filter by Status")
        filter_option = st.selectbox("Select Status", ["All", "Open", "Claimed", "Delivered"])
        if filter_option != "All":
            df = df[df["status"] == filter_option]

        st.dataframe(df)

        # --- Claimed donations summary ---
        st.markdown("### 🏢 Claimed Donations Summary")
        claimed_df = df[df["status"].str.contains("Claimed", na=False)]
        if claimed_df.empty:
            st.info("No donations have been claimed yet.")
        else:
            cols_show = [c for c in ["donation_id", "donor_name", "ngo_name", "claimed_at", "food_description"] if c in claimed_df.columns]
            st.table(claimed_df[cols_show])

        # --- Donor → NGO Claim Workflow (also allow claim from dashboard) ---
        st.markdown("### 🤝 Claim a Donation")
        donation_id_claim = st.number_input("Enter Donation ID to claim", min_value=1, step=1, key="claim_id")
        ngo_name = st.text_input("NGO Name", key="ngo_name_input_dashboard")
        ngo_contact = st.text_input("NGO Contact (optional)", key="ngo_contact_input_dashboard")

        if st.button("Claim Donation (Dashboard)"):
            try:
                resp = api_claim_donation(donation_id_claim, ngo_name, ngo_contact)
                st.success(f"Donation {donation_id_claim} successfully claimed by {ngo_name}.")
                st.json(resp)
                st.experimental_rerun()
            except Exception:
                st.error("❌ Could not claim donation — check backend endpoints and ID.")

        # --- Mark Claimed Donations as Delivered ---
        st.markdown("### 📦 Mark Donation as Delivered")
        donation_id_deliver = st.number_input("Enter Claimed Donation ID", min_value=1, step=1, key="deliver_id_dashboard")

        if st.button("Mark as Delivered"):
            try:
                resp = api_mark_delivered(donation_id_deliver)
                st.success(f"Donation {donation_id_deliver} marked as Delivered.")
                st.json(resp)
                st.experimental_rerun()
            except Exception:
                st.error("❌ Could not mark as delivered — check backend endpoints and ID.")

# ----------------------------- #
# TAB 8: VOLUNTEER / DELIVERY COORDINATION
# ----------------------------- #
with tabs[7]:
    st.subheader("🚚 Volunteer / Delivery Coordination")

    st.markdown(
        """
        Visualize active deliveries, volunteer assignments and (if available) routes.
        This tab calls the backend delivery endpoints. If your delivery objects include coordinates,
        they will be plotted on the map.
        """
    )

    try:
        deliveries = api_get_deliveries()
    except Exception:
        st.error("❌ Could not load deliveries from backend. Make sure backend is running and STREAMLIT_API_URL is set.")
        st.stop()

    if not deliveries:
        st.info("No deliveries scheduled yet.")
    else:
        deliveries_df = pd.DataFrame(deliveries)
        st.dataframe(deliveries_df)

        show_routes = st.checkbox("Show map with delivery points & routes")
        if show_routes:
            m = folium.Map(location=[30.3753, 69.3451], zoom_start=5)
            for d in deliveries:
                # expecting each delivery may have pickup_coords and dropoff_coords as [lat,lon]
                pickup = d.get("pickup_coords") or d.get("pickup_latlon")
                dropoff = d.get("dropoff_coords") or d.get("dropoff_latlon")
                volunteer = d.get("volunteer_name") or d.get("assigned_to")
                status = d.get("status", "scheduled")
                if pickup:
                    lat, lon = pickup if isinstance(pickup, (list, tuple)) else (None, None)
                    if lat and lon:
                        folium.Marker([lat, lon], popup=f"Pickup - {d.get('id','')}", icon=folium.Icon(color="green")).add_to(m)
                if dropoff:
                    lat2, lon2 = dropoff if isinstance(dropoff, (list, tuple)) else (None, None)
                    if lat2 and lon2:
                        folium.Marker([lat2, lon2], popup=f"Dropoff - {d.get('id','')}", icon=folium.Icon(color="blue")).add_to(m)
                # draw route line if both present
                try:
                    if pickup and dropoff and isinstance(pickup, (list, tuple)) and isinstance(dropoff, (list, tuple)):
                        folium.PolyLine([pickup, dropoff], color="orange", weight=3, opacity=0.8).add_to(m)
                except Exception:
                    pass
            st_folium(m, width=900, height=560)

    # Optionally show analytics
    if st.button("📈 Show quick analytics from backend"):
        try:
            analytics = api_get_analytics()
            st.json(analytics)
        except Exception:
            st.error("❌ Could not fetch analytics from backend.")

