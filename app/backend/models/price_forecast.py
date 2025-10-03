from typing import Optional, Tuple
import warnings
warnings.filterwarnings("ignore")

import pandas as pd

# Prophet import with fallback
try:
    from prophet import Prophet
    HAVE_PROPHET = True
except Exception:
    HAVE_PROPHET = False

# pmdarima import with fallback
try:
    import pmdarima as pm
    HAVE_PMDARIMA = True
except Exception:
    HAVE_PMDARIMA = False

# statsmodels fallback
try:
    import statsmodels.api as sm
    HAVE_STATSMODELS = True
except Exception:
    HAVE_STATSMODELS = False


def _prep_series(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    s = df[[date_col, value_col]].dropna().copy()
    s[date_col] = pd.to_datetime(s[date_col])
    s = s.sort_values(date_col)
    return s


def forecast_prophet(df: pd.DataFrame, date_col: str, value_col: str,
                     periods: int = 30, freq: str = "D") -> pd.DataFrame:
    if not HAVE_PROPHET:
        raise ImportError("Prophet is not available")
    s = _prep_series(df, date_col, value_col)
    train = s.rename(columns={date_col: "ds", value_col: "y"})
    m = Prophet(seasonality_mode="additive",
                weekly_seasonality=True,
                yearly_seasonality=True)
    m.fit(train)
    future = m.make_future_dataframe(periods=periods, freq=freq)
    fcst = m.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    return fcst


def forecast_arima_pmdarima(df: pd.DataFrame, date_col: str, value_col: str,
                            periods: int = 30, freq: str = "D") -> pd.DataFrame:
    if not HAVE_PMDARIMA:
        raise ImportError("pmdarima is not available")
    s = _prep_series(df, date_col, value_col)
    s = s.set_index(date_col).asfreq(freq).interpolate()
    model = pm.auto_arima(s[value_col], seasonal=False,
                          error_action="ignore", suppress_warnings=True)
    pred, ci = model.predict(n_periods=periods, return_conf_int=True)
    idx_future = pd.date_range(s.index.max() + pd.Timedelta(1, unit=freq.lower()[0]),
                               periods=periods, freq=freq)
    out = pd.DataFrame({
        "ds": list(s.index) + list(idx_future),
        "yhat": list(s[value_col]) + list(pred)
    })
    ci_df = pd.DataFrame(ci, columns=["yhat_lower", "yhat_upper"],
                         index=idx_future).reset_index(drop=True)
    hist_ci = pd.DataFrame({"yhat_lower": [None]*len(s), "yhat_upper": [None]*len(s)})
    out_ci = pd.concat([hist_ci, ci_df], ignore_index=True)
    return pd.concat([out, out_ci], axis=1)


def forecast_arima_statsmodels(df: pd.DataFrame, date_col: str, value_col: str,
                               periods: int = 30, freq: str = "D") -> pd.DataFrame:
    if not HAVE_STATSMODELS:
        raise ImportError("statsmodels is not available")
    s = _prep_series(df, date_col, value_col)
    s = s.set_index(date_col).asfreq(freq).interpolate()
    model = sm.tsa.ARIMA(s[value_col], order=(1, 1, 1)).fit()
    forecast = model.get_forecast(steps=periods)
    pred = forecast.predicted_mean
    ci = forecast.conf_int()

    idx_future = pd.date_range(s.index.max() + pd.Timedelta(1, unit=freq.lower()[0]),
                               periods=periods, freq=freq)
    out = pd.DataFrame({
        "ds": list(s.index) + list(idx_future),
        "yhat": list(s[value_col]) + list(pred)
    })
    ci_df = ci.rename(columns={"lower y": "yhat_lower", "upper y": "yhat_upper"})
    ci_df = ci_df.reset_index(drop=True)
    hist_ci = pd.DataFrame({"yhat_lower": [None]*len(s), "yhat_upper": [None]*len(s)})
    out_ci = pd.concat([hist_ci, ci_df], ignore_index=True)
    return pd.concat([out, out_ci], axis=1)


def forecast_prices(
    df: pd.DataFrame,
    commodity: Optional[str] = None,
    market: Optional[str] = None,
    periods: int = 30,
    freq: str = "D",
    method: str = "prophet"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Expects df columns: date, commodity, market, price
    Filters commodity/market if provided; returns (filtered_history, forecast)
    """
    data = df.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna(subset=["date", "price"])

    if commodity:
        data = data[data["commodity"].str.lower() == commodity.lower()]
    if market:
        data = data[data["market"].str.lower() == market.lower()]

    if data.empty:
        raise ValueError("No data after filtering. Check commodity/market names.")

    # Choose method with fallbacks
    if method == "prophet" and HAVE_PROPHET:
        fcst = forecast_prophet(data, "date", "price", periods=periods, freq=freq)
    elif method == "arima" and HAVE_PMDARIMA:
        fcst = forecast_arima_pmdarima(data, "date", "price", periods=periods, freq=freq)
    elif HAVE_STATSMODELS:  # last resort fallback
        fcst = forecast_arima_statsmodels(data, "date", "price", periods=periods, freq=freq)
    else:
        raise ImportError("No forecasting library available (prophet, pmdarima, or statsmodels).")

    return data.sort_values("date"), fcst
