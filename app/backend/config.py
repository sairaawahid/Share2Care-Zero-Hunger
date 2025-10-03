# app/backend/config.py
from pathlib import Path

# ---- Base Paths ----
PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_RAW    = PROJECT_DIR / "app" / "data" / "raw"
DATA_PROC   = PROJECT_DIR / "app" / "data" / "processed"
MODELS_DIR  = PROJECT_DIR / "app" / "models"

# ---- Required Raw Data ----
# Pakistan Administrative Boundaries 
PAK_ADMIN_BOUNDARIES = DATA_RAW / "pak_admin_boundaries"

# OCHA Humanitarian Response – Food Security Cluster & 5W 
OCHA_5W_FILE = DATA_RAW / "OCHA_PAK_5W.xlsx"

# WFP food-price monitoring (CSV)
WFP_FOOD_PRICES = DATA_RAW / "wfp_food_prices_pak.csv"

# Pakistan IPC Acute Food Insecurity
IPC_PAK_AREA_CSV   = DATA_RAW / "ipc_pak_area_long.csv"
IPC_PAK_LEVEL1_CSV = DATA_RAW / "ipc_pak_level1_long.csv"
IPC_PAK_NATION_CSV = DATA_RAW / "ipc_pak_national_long.csv"
IPC_PAK_GEOJSON    = DATA_RAW / "ipc_pak.geojson"

# ---- Processed Outputs ----
MERGED_SEVERITY_GEOJSON = DATA_PROC / "pak_severity_map.geojson"   # from OCHA_5W_FILE
IPC_SEVERITY_GEOJSON    = DATA_PROC / "ipc_severity_map.geojson"
OCHA_5W_ADMIN_COUNTS    = DATA_PROC / "ocha_5w_admin_counts.csv"

# Models
IMGNET_LABELS_JSON = MODELS_DIR / "imagenet_labels.json"
