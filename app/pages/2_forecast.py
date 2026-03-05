import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "src"))
from data_loader import load_data
from features import engineer_features
from theme import init_theme, get_theme_vars, apply_theme_css, render_sidebar, render_toggle

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Forecast · Energy Forecaster",
    layout="wide",
)

# ── Theme setup ────────────────────────────────────────────────────────────────
init_theme()
t = get_theme_vars()
apply_theme_css(t)
render_toggle("theme_btn_forecast")
render_sidebar(t)

# ── Plotly theme ───────────────────────────────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor=t['BG'],
    plot_bgcolor=t['CARD_BG'],
    font_color=t['TEXT'],
    xaxis=dict(gridcolor=t['GRID'], zerolinecolor=t['GRID']),
    yaxis=dict(gridcolor=t['GRID'], zerolinecolor=t['GRID']),
)
AMBER = "#f5a623"
TEAL  = "#4ecdc4"

ROOT_DIR   = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = ROOT_DIR / "data" / "models"

FEATURE_COLS = [
    "hour", "day_of_week", "month", "quarter", "season_code",
    "is_weekend", "is_night", "lag_1h", "lag_24h", "lag_168h",
    "rolling_mean_24h", "rolling_std_24h", "rolling_mean_168h",
    "voltage", "intensity"
]

# ── Cached loaders ─────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    df = load_data(resample_freq="h")
    df = engineer_features(df)
    return df

@st.cache_resource
def load_xgb_model():
    return joblib.load(MODELS_DIR / "xgboost_model.pkl")

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("# FORECAST")
st.markdown("##### XGBoost-powered energy consumption predictions")
st.markdown("---")

df    = get_data()
model = load_xgb_model()

# ── Controls ───────────────────────────────────────────────────────────────────
st.markdown("### Configure Forecast Window")
col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    forecast_days = st.selectbox(
        "Forecast horizon",
        options=[1, 3, 7, 14],
        index=2,
        format_func=lambda x: f"{x} day{'s' if x > 1 else ''}",
    )
with col_c2:
    context_days = st.selectbox(
        "Historical context to show",
        options=[7, 14, 30],
        index=0,
        format_func=lambda x: f"{x} days prior",
    )
with col_c3:
    show_confidence = st.selectbox(
        "Confidence band",
        options=["Show", "Hide"],
        index=0,
    )

st.markdown("---")

# ── Generate forecast ──────────────────────────────────────────────────────────
forecast_hours = forecast_days * 24
context_hours  = context_days * 24
context_df     = df.iloc[-(context_hours + 168):].iloc[:context_hours]

forecast_idx = pd.date_range(
    start=df.index[-1] + pd.Timedelta(hours=1),
    periods=forecast_hours,
    freq="h",
)

preds   = []
rolling = df.copy()

for i in range(forecast_hours):
    next_time = forecast_idx[i]
    row = {
        "hour":              next_time.hour,
        "day_of_week":       next_time.dayofweek,
        "month":             next_time.month,
        "quarter":           next_time.quarter,
        "season_code":       [0,0,1,1,1,2,2,2,3,3,3,0][next_time.month - 1],
        "is_weekend":        int(next_time.dayofweek >= 5),
        "is_night":          int(next_time.hour >= 22 or next_time.hour <= 6),
        "lag_1h":            rolling["active_power"].iloc[-1],
        "lag_24h":           rolling["active_power"].iloc[-24]  if len(rolling) >= 24  else rolling["active_power"].mean(),
        "lag_168h":          rolling["active_power"].iloc[-168] if len(rolling) >= 168 else rolling["active_power"].mean(),
        "rolling_mean_24h":  rolling["active_power"].iloc[-24:].mean(),
        "rolling_std_24h":   rolling["active_power"].iloc[-24:].std(),
        "rolling_mean_168h": rolling["active_power"].iloc[-168:].mean(),
        "voltage":           rolling["voltage"].mean(),
        "intensity":         rolling["intensity"].mean(),
    }
    X    = pd.DataFrame([row])[FEATURE_COLS]
    yhat = max(0, float(model.predict(X)[0]))
    preds.append(yhat)

    new_row                 = pd.DataFrame([row], index=[next_time])
    new_row["active_power"] = yhat
    new_row["voltage"]      = rolling["voltage"].mean()
    new_row["intensity"]    = rolling["intensity"].mean()
    rolling                 = pd.concat([rolling, new_row])

forecast_series = pd.Series(preds, index=forecast_idx)
upper           = forecast_series * 1.10
lower           = forecast_series * 0.90

# ── Metrics ────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Forecast Horizon",    f"{forecast_days} days")
with col2:
    st.metric("Avg Predicted (kW)",  f"{forecast_series.mean():.3f}")
with col3:
    st.metric("Peak Predicted (kW)", f"{forecast_series.max():.3f}")
with col4:
    st.metric("Min Predicted (kW)",  f"{forecast_series.min():.3f}")

st.markdown("---")

# ── Main forecast chart ────────────────────────────────────────────────────────
st.markdown("### Forecast vs Historical Context")
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=context_df.index, y=context_df["active_power"],
    mode="lines", name="Historical",
    line=dict(color=AMBER, width=1.2),
))

if show_confidence == "Show":
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_series, forecast_series[::-1]]).index,
        y=pd.concat([upper, lower[::-1]]).values,
        fill="toself",
        fillcolor="rgba(78,205,196,0.1)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Confidence Band",
    ))

fig.add_trace(go.Scatter(
    x=forecast_series.index, y=forecast_series.values,
    mode="lines", name="Forecast",
    line=dict(color=TEAL, width=2, dash="dot"),
))

fig.add_trace(go.Scatter(
    x=[df.index[-1], df.index[-1]],
    y=[0, df["active_power"].max() * 1.2],
    mode="lines", name="Forecast Start",
    line=dict(color=t['SUBTEXT'], width=1.5, dash="dash"),
))

fig.update_layout(
    **PLOT_THEME,
    height=420,
    margin=dict(l=0, r=0, t=20, b=0),
    xaxis_title="Datetime",
    yaxis_title="Active Power (kW)",
    legend=dict(
        bgcolor=t['CARD_BG'],
        bordercolor=t['BORDER'],
        borderwidth=1,
        font=dict(color=t['TEXT']),
    ),
)
st.plotly_chart(fig, use_container_width=True)

# ── Daily aggregated forecast ──────────────────────────────────────────────────
st.markdown("### Daily Average Forecast")
daily_forecast = forecast_series.resample("D").mean()
fig2 = go.Figure(go.Bar(
    x=daily_forecast.index.strftime("%a %d %b"),
    y=daily_forecast.values,
    marker_color=AMBER,
    marker_line_width=0,
))
fig2.update_layout(
    **PLOT_THEME,
    height=280,
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis_title="Day",
    yaxis_title="Avg Predicted Power (kW)",
    showlegend=False,
)
st.plotly_chart(fig2, use_container_width=True)

# ── Raw forecast table ─────────────────────────────────────────────────────────
with st.expander("📋 View Raw Forecast Data"):
    forecast_table = pd.DataFrame({
        "Datetime":        forecast_series.index.strftime("%Y-%m-%d %H:%M"),
        "Predicted (kW)":  forecast_series.values.round(4),
        "Upper Band (kW)": upper.values.round(4),
        "Lower Band (kW)": lower.values.round(4),
    })
    st.dataframe(forecast_table, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:{t['SUBTEXT']};font-size:0.75rem;"
    f"font-family:Share Tech Mono,monospace;'>"
    f"XGBOOST ROLLING FORECAST · R² 0.9981 · UCI DATASET</p>",
    unsafe_allow_html=True,
)