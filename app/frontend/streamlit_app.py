import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
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
    "📝 Sentiment Analysis"
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
