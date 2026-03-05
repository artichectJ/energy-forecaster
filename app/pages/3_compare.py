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
from models.xgboost_model import FEATURE_COLS
from theme import init_theme, get_theme_vars, apply_theme_css, render_sidebar, render_toggle

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Model Comparison · Energy Forecaster",
    layout="wide",
)

# ── Theme setup ────────────────────────────────────────────────────────────────
init_theme()
t = get_theme_vars()
apply_theme_css(t)
render_toggle("theme_btn_compare")
render_sidebar(t)

# ── Plotly theme ───────────────────────────────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor=t['BG'],
    plot_bgcolor=t['CARD_BG'],
    font_color=t['TEXT'],
    xaxis=dict(gridcolor=t['GRID'], zerolinecolor=t['GRID']),
    yaxis=dict(gridcolor=t['GRID'], zerolinecolor=t['GRID']),
)
AMBER  = "#f5a623"
TEAL   = "#4ecdc4"
CORAL  = "#ff6b6b"
PURPLE = "#a78bfa"

ROOT_DIR   = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = ROOT_DIR / "data" / "models"

# ── Cached data & models ───────────────────────────────────────────────────────
@st.cache_data
def get_data():
    df = load_data(resample_freq="h")
    df = engineer_features(df)
    return df

@st.cache_resource
def load_models():
    xgb     = joblib.load(MODELS_DIR / "xgboost_model.pkl")
    prophet = joblib.load(MODELS_DIR / "prophet_model.pkl")
    arima   = joblib.load(MODELS_DIR / "arima_model.pkl")
    return xgb, prophet, arima

@st.cache_data
def get_predictions(_xgb, _prophet, df):
    split_idx    = int(len(df) * 0.8)
    test_df      = df.iloc[split_idx:]
    xgb_preds    = _xgb.predict(test_df[FEATURE_COLS])
    prophet_df   = test_df[["active_power"]].reset_index()
    prophet_df.columns = ["ds", "y"]
    prophet_df["hour"]             = test_df["hour"].values
    prophet_df["is_weekend"]       = test_df["is_weekend"].values
    prophet_df["rolling_mean_24h"] = test_df["rolling_mean_24h"].values
    prophet_df["lag_24h"]          = test_df["lag_24h"].values
    forecast      = _prophet.predict(prophet_df)
    prophet_preds = np.clip(forecast["yhat"].values, 0, None)
    arima_actuals = test_df["active_power"].iloc[:200]
    return test_df, xgb_preds, prophet_preds, arima_actuals

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("# MODEL COMPARISON")
st.markdown("##### XGBoost vs Prophet vs ARIMA — head to head")
st.markdown("---")

with st.spinner("Loading models and generating predictions..."):
    df                                               = get_data()
    xgb, prophet, arima                              = load_models()
    test_df, xgb_preds, prophet_preds, arima_actuals = get_predictions(xgb, prophet, df)

# ── Metrics table ──────────────────────────────────────────────────────────────
st.markdown("### Performance Metrics")
metrics_df = pd.DataFrame({
    "Model":    ["XGBoost",       "Prophet",        "ARIMA"],
    "MAE":      [0.0202,           0.4533,            0.4414],
    "RMSE":     [0.0314,           0.5964,            0.6236],
    "R²":       [0.9981,           0.3290,            0.5275],
    "Speed":    ["⚡ Seconds",     "🕐 Minutes",      "🐢 Hours"],
    "Best For": ["Short-term hourly", "Long-term trends", "Univariate series"],
})
st.dataframe(metrics_df, use_container_width=True, hide_index=True)
st.markdown("---")

# ── Metric bar charts ──────────────────────────────────────────────────────────
st.markdown("### Visual Metric Comparison")
col1, col2, col3 = st.columns(3)
models  = ["XGBoost", "Prophet", "ARIMA"]
colours = [AMBER, TEAL, CORAL]

with col1:
    st.markdown("#### MAE ↓ lower is better")
    fig = go.Figure(go.Bar(
        x=models, y=[0.0202, 0.4533, 0.4414],
        marker_color=colours, marker_line_width=0,
        text=[0.0202, 0.4533, 0.4414],
        textposition="outside",
        textfont=dict(color=t['TEXT']),
    ))
    fig.update_layout(**PLOT_THEME, height=280,
                      margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### RMSE ↓ lower is better")
    fig = go.Figure(go.Bar(
        x=models, y=[0.0314, 0.5964, 0.6236],
        marker_color=colours, marker_line_width=0,
        text=[0.0314, 0.5964, 0.6236],
        textposition="outside",
        textfont=dict(color=t['TEXT']),
    ))
    fig.update_layout(**PLOT_THEME, height=280,
                      margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col3:
    st.markdown("#### R² ↑ higher is better")
    fig = go.Figure(go.Bar(
        x=models, y=[0.9981, 0.3290, 0.5275],
        marker_color=colours, marker_line_width=0,
        text=[0.9981, 0.3290, 0.5275],
        textposition="outside",
        textfont=dict(color=t['TEXT']),
    ))
    fig.update_layout(**PLOT_THEME, height=280,
                      margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── Predictions vs actuals ─────────────────────────────────────────────────────
st.markdown("### Predictions vs Actuals — First 200 Test Hours")
st.markdown("Zoomed in to first 200 hours for clarity across all three models.")

actuals     = test_df["active_power"].iloc[:200]
xgb_200     = xgb_preds[:200]
prophet_200 = prophet_preds[:200]
idx         = test_df.index[:200]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=idx, y=actuals.values,
    mode="lines", name="Actual",
    line=dict(color=t['SUBTEXT'], width=1.5),
))
fig2.add_trace(go.Scatter(
    x=idx, y=xgb_200,
    mode="lines", name="XGBoost",
    line=dict(color=AMBER, width=1.5),
))
fig2.add_trace(go.Scatter(
    x=idx, y=prophet_200,
    mode="lines", name="Prophet",
    line=dict(color=TEAL, width=1.5, dash="dot"),
))
fig2.update_layout(
    **PLOT_THEME,
    height=400,
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
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── Analysis ───────────────────────────────────────────────────────────────────
st.markdown("### Why These Results?")
col_l, col_r = st.columns(2)

with col_l:
    st.markdown("#### Why XGBoost Won")
    st.markdown("""
    XGBoost dominates because of **lag features** — giving the model direct access
    to consumption 1 hour, 24 hours, and 168 hours ago. Energy consumption is
    highly autocorrelated, meaning the recent past is the strongest predictor
    of the near future.

    Combined with 500 gradient boosted trees running in parallel across all
    CPU cores, XGBoost achieves near-perfect accuracy in seconds.
    """)
    st.markdown("#### Why ARIMA Was Slow")
    st.markdown("""
    ARIMA refits a full statistical model from scratch at every single forecast
    step. On 6,885 test hours this would take **15+ hours**. We limited it to
    200 steps — a deliberate engineering tradeoff between accuracy and
    practicality. In production, ARIMA is never used for thousands of steps.
    """)

with col_r:
    st.markdown("#### Why Prophet Underperformed")
    st.markdown("""
    Prophet is designed for **business metrics** — smooth, slowly-changing
    series like daily active users or monthly revenue. Household energy
    consumption has sharp, irregular spikes (appliances turning on/off)
    that Prophet's curve-fitting approach simply cannot capture.

    Prophet would outperform on a **monthly or yearly** aggregation of
    the same data where trend and seasonality dominate.
    """)
    st.markdown("#### Key Takeaway")
    st.markdown("""
    **Model selection is always dataset-dependent.** There is no universally
    best model. XGBoost wins here because the data is feature-rich and
    highly autocorrelated at the hourly level. On a different dataset —
    say, yearly national energy demand — Prophet might win convincingly.
    """)

st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:{t['SUBTEXT']};font-size:0.75rem;"
    f"font-family:Share Tech Mono,monospace;'>"
    f"XGBOOST · PROPHET · ARIMA · MODEL COMPARISON · UCI DATASET</p>",
    unsafe_allow_html=True,
)