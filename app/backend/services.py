from pathlib import Path
import pandas as pd
import geopandas as gpd

from .config import (
    MERGED_SEVERITY_GEOJSON, IPC_SEVERITY_GEOJSON,
    OCHA_5W_FILE, WFP_FOOD_PRICES
)
from .data_loader import (
    build_all_core_processed, load_wfp_prices
)
from .models.price_forecast import forecast_prices
from .models.image_tagging import tag_image_bytes
from .models.sentiment import analyze_text

def ensure_processed_maps():
    # Build processed files if missing
    need_build = False
    for p in [MERGED_SEVERITY_GEOJSON, IPC_SEVERITY_GEOJSON]:
        if not Path(p).exists():
            need_build = True
    if need_build:
        build_all_core_processed()
    return Path(MERGED_SEVERITY_GEOJSON), Path(IPC_SEVERITY_GEOJSON)

def get_wfp_prices_df() -> pd.DataFrame:
    return load_wfp_prices(WFP_FOOD_PRICES)

def get_price_forecast(df: pd.DataFrame, commodity: str, market: str, periods: int = 30, method: str = "prophet"):
    hist, fc = forecast_prices(df, commodity=commodity, market=market, periods=periods, method=method)
    return hist, fc

def tag_image(b: bytes):
    return tag_image_bytes(b, top_k=3)

def analyze_reflection(text: str):
    return analyze_text(text)
