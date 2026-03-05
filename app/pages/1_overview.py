import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent / "src"))
from data_loader import load_data
from features import engineer_features
from theme import init_theme, get_theme_vars, apply_theme_css, render_sidebar, render_toggle

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Overview · Energy Forecaster",
    layout="wide",
)

# ── Theme setup (3 lines, same on every page) ──────────────────────────────────
init_theme()
t = get_theme_vars()
apply_theme_css(t)
render_toggle("theme_btn_overview")
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

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    df = load_data(resample_freq="h")
    df = engineer_features(df)
    return df

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown("# HISTORICAL OVERVIEW")
st.markdown("##### Explore 4 years of household energy consumption patterns")
st.markdown("---")

with st.spinner("Loading dataset..."):
    df = get_data()

# ── Summary metrics ────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Avg Hourly Consumption", f"{df['active_power'].mean():.3f} kW")
with col2:
    st.metric("Peak Consumption",       f"{df['active_power'].max():.3f} kW")
with col3:
    st.metric("Min Consumption",        f"{df['active_power'].min():.3f} kW")
with col4:
    st.metric("Std Deviation",          f"{df['active_power'].std():.3f} kW")

st.markdown("---")

# ── 1. Full time series ────────────────────────────────────────────────────────
st.markdown("### Full Time Series — Active Power (kW)")
daily = df["active_power"].resample("D").mean()
fig1  = go.Figure()
fig1.add_trace(go.Scatter(
    x=daily.index, y=daily.values,
    mode="lines",
    line=dict(color=AMBER, width=1.2),
    fill="tozeroy",
    fillcolor="rgba(245,166,35,0.08)",
    name="Daily Avg",
))
fig1.update_layout(
    **PLOT_THEME, height=280,
    margin=dict(l=0, r=0, t=10, b=0),
    showlegend=False,
    xaxis_title="Date", yaxis_title="Active Power (kW)",
)
st.plotly_chart(fig1, use_container_width=True)

# ── 2. Hourly & weekly patterns ────────────────────────────────────────────────
st.markdown("### Consumption Patterns")
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### By Hour of Day")
    hourly_avg = df.groupby("hour")["active_power"].mean()
    fig2 = go.Figure(go.Bar(
        x=hourly_avg.index, y=hourly_avg.values,
        marker_color=[AMBER if v == hourly_avg.max() else t['BORDER']
                      for v in hourly_avg.values],
        marker_line_width=0,
    ))
    fig2.update_layout(**PLOT_THEME, height=300,
                       margin=dict(l=0, r=0, t=10, b=0),
                       xaxis_title="Hour of Day",
                       yaxis_title="Avg Active Power (kW)", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.markdown("#### By Day of Week")
    days    = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_avg = df.groupby("day_of_week")["active_power"].mean()
    fig3 = go.Figure(go.Bar(
        x=days, y=day_avg.values,
        marker_color=[AMBER if v == day_avg.max() else t['BORDER']
                      for v in day_avg.values],
        marker_line_width=0,
    ))
    fig3.update_layout(**PLOT_THEME, height=300,
                       margin=dict(l=0, r=0, t=10, b=0),
                       xaxis_title="Day of Week",
                       yaxis_title="Avg Active Power (kW)", showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

# ── 3. Seasonal breakdown ──────────────────────────────────────────────────────
st.markdown("### Seasonal & Monthly Breakdown")
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.markdown("#### By Season")
    season_avg = df.groupby("season")["active_power"].mean().reindex(
        ["Winter", "Spring", "Summer", "Autumn"]
    )
    fig4 = go.Figure(go.Bar(
        x=season_avg.index, y=season_avg.values,
        marker_color=[AMBER, TEAL, CORAL, PURPLE],
        marker_line_width=0,
    ))
    fig4.update_layout(**PLOT_THEME, height=300,
                       margin=dict(l=0, r=0, t=10, b=0),
                       xaxis_title="Season",
                       yaxis_title="Avg Active Power (kW)", showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

with col_r2:
    st.markdown("#### By Month")
    months    = ["Jan","Feb","Mar","Apr","May","Jun",
                 "Jul","Aug","Sep","Oct","Nov","Dec"]
    month_avg = df.groupby("month")["active_power"].mean()
    fig5 = go.Figure(go.Bar(
        x=months, y=month_avg.values,
        marker_color=[AMBER if v == month_avg.max() else t['BORDER']
                      for v in month_avg.values],
        marker_line_width=0,
    ))
    fig5.update_layout(**PLOT_THEME, height=300,
                       margin=dict(l=0, r=0, t=10, b=0),
                       xaxis_title="Month",
                       yaxis_title="Avg Active Power (kW)", showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)

# ── 4. Sub-metering breakdown ──────────────────────────────────────────────────
st.markdown("### Sub-Metering Breakdown")
st.markdown("Where is the energy actually going?")
sub_means = {
    "Kitchen": df["kitchen"].mean(),
    "Laundry": df["laundry"].mean(),
    "HVAC":    df["hvac"].mean(),
}
fig6 = go.Figure(go.Pie(
    labels=list(sub_means.keys()),
    values=list(sub_means.values()),
    hole=0.55,
    marker=dict(colors=[AMBER, TEAL, CORAL]),
    textfont=dict(color=t['TEXT']),
))
fig6.update_layout(
    **PLOT_THEME, height=320,
    margin=dict(l=0, r=0, t=10, b=0),
    showlegend=True,
    legend=dict(font=dict(color=t['TEXT'])),
)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.markdown(
    f"<p style='text-align:center;color:{t['SUBTEXT']};font-size:0.75rem;"
    f"font-family:Share Tech Mono,monospace;'>"
    f"UCI HOUSEHOLD POWER CONSUMPTION · HISTORICAL OVERVIEW</p>",
    unsafe_allow_html=True,
)