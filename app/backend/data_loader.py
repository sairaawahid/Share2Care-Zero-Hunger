from pathlib import Path
from typing import Optional, Tuple, List
import re
import pandas as pd
import geopandas as gpd

from .config import (
    DATA_PROC,
    PAK_ADMIN_BOUNDARIES,
    OCHA_5W_FILE,
    WFP_FOOD_PRICES,
    IPC_PAK_GEOJSON,
    MERGED_SEVERITY_GEOJSON,
    IPC_SEVERITY_GEOJSON,
    OCHA_5W_ADMIN_COUNTS,
)

# ---------- Helpers ----------
def _lower_cols(df):
    df = df.copy()
    df.columns = [c.lower().strip() for c in df.columns]
    return df

def _infer_admin_code_col(df) -> Optional[str]:
    for c in ["adm2_pcode","admin2pcode","admin2_pcode","adm1_pcode","admin1pcode","pcode","code"]:
        if c in df.columns: return c
    return None

def _safe_to_geojson(gdf: gpd.GeoDataFrame, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out_path, driver="GeoJSON")
    return out_path

# ---------- Admin Boundaries ----------
def load_admin_boundaries() -> gpd.GeoDataFrame:
    base = Path(PAK_ADMIN_BOUNDARIES)
    shp_list = list(base.glob("*adm2*.shp")) or list(base.glob("*adm1*.shp"))
    if not shp_list:
        raise FileNotFoundError("No ADM1/ADM2 shapefile found in pak_admin_boundaries/")
    gdf = gpd.read_file(shp_list[0])
    gdf = _lower_cols(gdf)
    code_col = _infer_admin_code_col(gdf)
    if code_col:
        gdf["admin_code"] = gdf[code_col].astype(str).str.upper()
    else:
        raise ValueError("No admin code in boundaries shapefile.")
    return gdf

# ---------- OCHA 5W / Food Security ----------
def load_ocha_5w(path: Optional[Path] = None) -> pd.DataFrame:
    path = Path(path or OCHA_5W_FILE)
    if path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    df = _lower_cols(df)
    return df

def build_severity_from_ocha() -> gpd.GeoDataFrame:
    """Derive a severity score from OCHA 5W Excel (people in need or IPC phase)."""
    ocha = load_ocha_5w()
    code_col = _infer_admin_code_col(ocha)
    if not code_col:
        raise ValueError("Cannot find admin code column in OCHA 5W.")
    ocha["admin_code"] = ocha[code_col].astype(str).str.upper()

    # Create severity_score
    if "severity" in ocha.columns:
        ocha["severity_score"] = ocha["severity"]
    elif "ipc_phase" in ocha.columns:
        ocha["severity_score"] = ocha["ipc_phase"]
    else:
        pin_col = next((c for c in ["people_in_need","pin","targeted"] if c in ocha.columns), None)
        if pin_col:
            m = ocha[pin_col].max() or 1
            ocha["severity_score"] = (ocha[pin_col] / m) * 5.0
        else:
            ocha["severity_score"] = 1.0

    keep = ["admin_code","severity_score"]
    return ocha[keep].drop_duplicates("admin_code")

def build_and_export_severity_geojson(out_path: Optional[Path] = None) -> Path:
    b = load_admin_boundaries()
    fsc = build_severity_from_ocha()
    merged = b.merge(fsc, on="admin_code", how="left")
    merged["severity_score"] = merged["severity_score"].fillna(0)
    return _safe_to_geojson(merged, out_path or MERGED_SEVERITY_GEOJSON)

# ---------- IPC Acute Food Insecurity ----------
def build_and_export_ipc_geojson(out_path: Optional[Path] = None) -> Path:
    path = Path(IPC_PAK_GEOJSON)
    ipc = gpd.read_file(path)
    ipc = _lower_cols(ipc)
    phase_col = next((c for c in ["ipc_phase","phase","phase_num"] if c in ipc.columns), None)
    if phase_col:
        ipc["severity_score"] = ipc[phase_col]
    else:
        ipc["severity_score"] = 0
    return _safe_to_geojson(ipc, out_path or IPC_SEVERITY_GEOJSON)

# ---------- WFP Prices ----------
def load_wfp_prices(path: Optional[Path] = None) -> pd.DataFrame:
    path = Path(path or WFP_FOOD_PRICES)
    df = pd.read_csv(path)
    df = _lower_cols(df)
    date_col = next((c for c in ["date","month"] if c in df.columns), None)
    price_col = next((c for c in ["price","value","avg_price"] if c in df.columns), None)
    comm_col = next((c for c in ["commodity","item"] if c in df.columns), None)
    market_col = next((c for c in ["market","location","city"] if c in df.columns), None)
    out = df[[date_col, comm_col, market_col, price_col]].rename(
        columns={date_col:"date", comm_col:"commodity", market_col:"market", price_col:"price"}
    )
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    return out.dropna(subset=["date","price"]).sort_values("date")

# ---------- Build All ----------
def build_all_core_processed():
    paths = {}
    paths["ocha_fsc_geojson"] = build_and_export_severity_geojson()
    paths["ipc_geojson"]      = build_and_export_ipc_geojson()
    return paths
