import io
import json
import math
import time
import pandas as pd
import geopandas as gpd
import folium
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_folium import st_folium

from app.backend.services import (
    ensure_processed_maps,
    get_wfp_prices_df,
    get_price_forecast,
    tag_image,
    analyze_reflection,
)

st.set_page_config(page_title="Share2Care – Zero Hunger", layout="wide")

st.title("Share2Care – Zero Hunger")
st.caption("Pakistan • OCHA FSC & IPC overlays • WFP prices • Behavioral nudges • AI helpers")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["🗺️ Map", "📈 Prices & Forecast", "🤝 Pledges & Mood", "🖼️ Image Tagging"])

# ---------- Helpers ----------
@st.cache_data(show_spinner=False)
def load_geojson(path):
    return gpd.read_file(path)

def color_for_score(x):
    # simple 0–5 scale to color
    # 0: gray, 1–2: yellow/orange, 3–4: red, 5: dark red
    try:
        x = float(x)
    except:
        x = 0.0
    if x <= 0: return "#bdbdbd"
    if x <= 1: return "#ffe082"
    if x <= 2: return "#ffb74d"
    if x <= 3: return "#ff8a65"
    if x <= 4: return "#e57373"
    return "#c62828"

# ---------- Page: Map ----------
if page == "🗺️ Map":
    st.subheader("Need Map: OCHA FSC severity (base) + IPC overlay (optional)")

    # Ensure processed files exist
    base_path, ipc_path = ensure_processed_maps()
    # Load
    gdf_base = load_geojson(str(base_path))
    gdf_ipc  = load_geojson(str(ipc_path))

    # Center on Pakistan
    m = folium.Map(location=[30.3753, 69.3451], zoom_start=5, tiles="cartodbpositron")

    # Base layer (FSC severity)
    def style_func(feature):
        s = feature["properties"].get("severity_score", 0)
        return {"fillColor": color_for_score(s), "color": "#555", "weight": 0.5, "fillOpacity": 0.6}

    folium.GeoJson(
        json.loads(gdf_base.to_json()),
        name="FSC Severity",
        style_function=style_func,
        tooltip=folium.GeoJsonTooltip(fields=[k for k in gdf_base.columns if k != "geometry"][:8])
    ).add_to(m)

    # Optional IPC overlay toggle
    show_ipc = st.checkbox("Show IPC overlay", value=True)
    if show_ipc:
        def style_ipc(feature):
            s = feature["properties"].get("severity_score", 0)
            return {"fillColor": color_for_score(s), "color": "#111", "weight": 0.5, "fillOpacity": 0.35}
        folium.GeoJson(
            json.loads(gdf_ipc.to_json()),
            name="IPC Acute Food Insecurity",
            style_function=style_ipc,
            tooltip=folium.GeoJsonTooltip(fields=[k for k in gdf_ipc.columns if k != "geometry"][:8])
        ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, use_container_width=True, height=600)

    st.info("Tip: The color scale reflects a 0–5 severity score. Toggle the IPC overlay to compare.")

# ---------- Page: Prices & Forecast ----------
elif page == "📈 Prices & Forecast":
    st.subheader("WFP Food Price Monitoring")

    df = get_wfp_prices_df()
    commodities = sorted(df["commodity"].dropna().unique().tolist())
    markets     = sorted(df["market"].dropna().unique().tolist())

    c1, c2, c3 = st.columns([2,2,1])
    with c1:
        commodity = st.selectbox("Commodity", options=commodities, index=0 if commodities else None)
    with c2:
        market = st.selectbox("Market", options=markets, index=0 if markets else None)
    with c3:
        periods = st.number_input("Forecast days", min_value=7, max_value=180, value=30, step=7)

    if commodity and market:
        # Historical
        hist = df[(df["commodity"].str.lower()==commodity.lower()) & (df["market"].str.lower()==market.lower())]
        if hist.empty:
            st.warning("No data for that commodity/market.")
        else:
            st.write(f"Latest observation: **{hist['date'].max().date()}** | Rows: {len(hist)}")

            # Forecast (Prophet if available, else ARIMA)
            method = st.selectbox("Method", ["prophet","arima"], index=0)
            try:
                hist_f, fc = get_price_forecast(df, commodity, market, periods=int(periods), method=method)

                # Plot
                fig, ax = plt.subplots(figsize=(8,4))
                ax.plot(hist_f["date"], hist_f["price"], label="History")
                ax.plot(fc["ds"], fc["yhat"], label="Forecast")
                if "yhat_lower" in fc.columns and "yhat_upper" in fc.columns:
                    ax.fill_between(fc["ds"], fc["yhat_lower"], fc["yhat_upper"], alpha=0.2)
                ax.set_xlabel("Date"); ax.set_ylabel("Price")
                ax.legend()
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Forecast error: {e}")

# ---------- Page: Pledges & Mood ----------
elif page == "🤝 Pledges & Mood":
    st.subheader("Build a helping habit")

    if "pledge" not in st.session_state: st.session_state.pledge = 2
    if "donations" not in st.session_state: st.session_state.donations = 0
    if "streak" not in st.session_state: st.session_state.streak = 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.pledge = st.number_input("Meals pledged this week", 0, 100, st.session_state.pledge)
    with c2:
        if st.button("Log 1 meal donated"):
            st.session_state.donations += 1
            if st.session_state.donations % st.session_state.pledge == 0 and st.session_state.pledge > 0:
                st.session_state.streak += 1
    with c3:
        if st.button("Reset week"):
            st.session_state.donations = 0

    st.metric("Meals donated this week", st.session_state.donations)
    st.metric("Weekly pledge", st.session_state.pledge)
    st.metric("Streak", st.session_state.streak)

    st.divider()
    st.write("**Reflection (optional):** How do you feel after donating?")
    text = st.text_area("Write 1–2 sentences…")
    if st.button("Analyze mood"):
        res = analyze_reflection(text)
        st.success(f"Mood: **{res['label']}** (confidence {res['score']:.2f})")
        if res["label"].upper().startswith("POS"):
            st.balloons()
            st.info("Altruism boost: Positive reflections make habits stick!")

# ---------- Page: Image Tagging ----------
elif page == "🖼️ Image Tagging":
    st.subheader("Auto-tag food images (demo)")
    up = st.file_uploader("Upload a food image", type=["jpg","jpeg","png"])
    if up:
        st.image(up, use_column_width=True)
        with st.spinner("Tagging…"):
            tags = tag_image(up.read())
        st.write("Top predictions:")
        for lbl, prob in tags:
            st.write(f"• **{lbl}** — {prob:.2f}")
