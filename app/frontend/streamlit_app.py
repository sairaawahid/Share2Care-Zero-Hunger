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

# --- Donor–NGO Workflow Imports ---
from app.backend.workflow.donor import submit_donation
from app.backend.workflow.ngo import view_and_claim_donations, claim_donation

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

# -------------------------------------------
# Donor–NGO Workflow Helper Functions
# -------------------------------------------
DATA_FILE = "donations.json"

def load_donations():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    return data

def save_donations(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def submit_donation(donor_name, contact, location, food_desc, mood, food_img):
    data = load_donations()
    donation_id = len(data) + 1
    record = {
        "donation_id": donation_id,
        "donor_name": donor_name,
        "contact": contact,
        "location": location,
        "food_desc": food_desc,
        "mood": mood,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Available",
        "claimed_by": None
    }
    if food_img:
        record["food_img"] = food_img.name
    data.append(record)
    save_donations(data)
    return record

def view_donations_df():
    data = load_donations()
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

def claim_donation(donation_id, ngo_name):
    data = load_donations()
    for d in data:
        if d["donation_id"] == donation_id and d["status"] == "Available":
            d["status"] = "Claimed"
            d["claimed_by"] = ngo_name
            d["claimed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_donations(data)
            return d
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
    "🤝 NGO Dashboard"
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
            fcst = forecast_prices(df_sel, periods=60)
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
                result = submit_donation(donor_name, contact, location, food_desc, mood, food_img)
                st.success("✅ Donation submitted successfully!")
                st.json(result)

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

        df_donations = view_donations_df()
        available_df = df_donations[df_donations["status"] == "Available"] if not df_donations.empty else pd.DataFrame()

        if available_df.empty:
            st.info("No unclaimed donations available right now.")
        else:
            st.dataframe(available_df)
            selected_id = st.selectbox("Select Donation ID to Claim:", available_df["donation_id"].tolist())
            ngo_name = st.text_input("Enter your NGO Name")

            if st.button("Claim Selected Donation"):
                if ngo_name.strip():
                    claimed = claim_donation(selected_id, ngo_name)
                    if claimed:
                        st.success(f"✅ Donation ID {selected_id} has been claimed by {ngo_name}!")
                    else:
                        st.warning("⚠️ That donation may have already been claimed.")
                else:
                    st.error("Please enter your NGO name before claiming.")

# ----------------------------- #
# TAB 7: NGO DASHBOARD
# ----------------------------- #
with tabs[6]:
    st.subheader("📊 NGO Dashboard — Donation Status Overview")

    df = view_donations_df()

    if df.empty:
        st.info("No donations submitted yet.")
    else:
        # --- Full data table ---
        st.dataframe(df)

        # --- Filter by status ---
        st.markdown("### 🔍 Filter by Status")
        filter_option = st.selectbox("Select Status", ["All", "Available", "Claimed"])
        if filter_option != "All":
            df = df[df["status"] == filter_option]

        st.dataframe(df)

        # --- Claimed donations summary ---
        st.markdown("### 🏢 Claimed Donations Summary")
        claimed_df = df[df["status"] == "Claimed"]
        if claimed_df.empty:
            st.info("No donations have been claimed yet.")
        else:
            st.table(
                claimed_df[
                    ["donation_id", "donor_name", "claimed_by", "claimed_at", "food_desc"]
                ]
            )

        # ---------- Optional Cached Map View for NGO Dashboard ----------
        show_map = st.checkbox("🗺️ Show Map View of Donations")

        if show_map and not df.empty:
            st.markdown("### 📍 Donation Pickup Locations")

            # Initialize base map (Pakistan-centered)
            m = folium.Map(location=[30.3753, 69.3451], zoom_start=5)

            # Define status-based colors and badges
            status_colors = {
                "Available": "green",
                "Claimed": "blue",
                "Delivered": "gray",
            }

            for _, row in df.iterrows():
                location_text = str(row["location"])
                donation_id = row.get("donation_id", "N/A")
                donor_name = row.get("donor_name", "Unknown Donor")
                food_desc = row.get("food_desc", "No description")  # ✅ corrected key
                status = row.get("status", "Available")
                ngo = row.get("claimed_by", "—")

                coords = geocode_location_cached(location_text)
                if coords:
                    lat, lon = coords

                    # Badge color and HTML popup
                    color = status_colors.get(status, "lightgray")
                    popup_html = f"""
                    <div style='font-size:14px; line-height:1.4'>
                    <b>Donation ID:</b> {donation_id}<br>
                    <b>Donor:</b> {donor_name}<br>
                    <b>Food:</b> {food_desc}<br>
                    <b>Claimed By:</b> {ngo}<br>
                    <b>Status:</b> <span style='color:white; background:{color}; 
                    padding:2px 6px; border-radius:4px;'>{status}</span>
                    </div>
                    """

                    folium.Marker(
                        [lat, lon],
                        popup=popup_html,
                        icon=folium.Icon(color=color, icon="cutlery", prefix="fa"),
                    ).add_to(m)

            # Add legend to map
            legend_html = """
            <div style="
                position: fixed; 
                bottom: 30px; left: 30px; width: 160px; height: 110px; 
                background-color: white; z-index:9999; font-size:14px; 
                border-radius:8px; box-shadow:0 0 6px rgba(0,0,0,0.3);
                padding: 10px;">
                <b>🗺️ Legend</b><br>
                <i style="background:green;width:10px;height:10px;float:left;margin-right:8px;margin-top:4px;"></i> Available<br>
                <i style="background:blue;width:10px;height:10px;float:left;margin-right:8px;margin-top:4px;"></i> Claimed<br>
                <i style="background:gray;width:10px;height:10px;float:left;margin-right:8px;margin-top:4px;"></i> Delivered<br>
            </div>
            """
            m.get_root().html.add_child(folium.Element(legend_html))

            # Display map
            st_folium(m, width=750, height=480)
