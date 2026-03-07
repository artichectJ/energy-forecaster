# ⚡ Energy Forecaster

A production-grade household energy consumption forecasting application built
with Python, featuring three ML models and an interactive Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.55-red)
![XGBoost](https://img.shields.io/badge/XGBoost-R²%200.9981-green)

## 🔍 Overview
This app analyses 4 years of minute-level household electricity consumption
from the UCI Machine Learning Repository, resampled to hourly granularity
for meaningful forecasting and pattern analysis.

## 📊 Models Implemented
| Model | MAE | RMSE | R² | Speed |
|-------|-----|------|----|-------|
| XGBoost | 0.0202 | 0.0314 | 0.9981 | Seconds |
| ARIMA | 0.4414 | 0.6236 | 0.5275 | Minutes |
| Prophet | 0.4533 | 0.5964 | 0.3290 | Minutes |

## 🗂️ Project Structure
```
energy-forecaster/
├── data/raw/                 # UCI dataset
├── src/
│   ├── data_loader.py        # Data pipeline
│   ├── features.py           # Feature engineering
│   ├── theme.py              # App theming
│   └── models/
│       ├── xgboost_model.py
│       ├── prophet_model.py
│       └── arima_model.py
├── app/
│   ├── main.py               # Home page
│   └── pages/
│       ├── 1_overview.py     # Historical trends
│       ├── 2_forecast.py     # Forecasting
│       └── 3_compare.py      # Model comparison
└── requirements.txt
```

## 🚀 Running Locally
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/energy-forecaster.git
cd energy-forecaster

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download the dataset
# UCI Household Power Consumption:
# https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption
# Place household_power_consumption.txt in data/raw/

# Train the models
python src/models/xgboost_model.py
python src/models/prophet_model.py
python src/models/arima_model.py

# Launch the app
streamlit run app/main.py
```

## 🖥️ How to Use

### Home
Landing page with project overview and key metrics. Use the **🌙 / ☀️ toggle** 
in the top right to switch between dark and light mode — preference persists 
across all pages.

### Historical Overview
Explore 4 years of consumption patterns broken down by:
- **Full time series** — daily average active power from 2006–2010
- **Hour of day** — identify peak usage hours (typically 18:00–21:00)
- **Day of week** — compare weekday vs weekend patterns
- **Season & month** — understand how weather drives consumption
- **Sub-metering** — see which appliances consume the most energy

### Forecast
Configure and run an XGBoost rolling forecast:
1. Select a **forecast horizon** (1, 3, 7, or 14 days)
2. Choose how much **historical context** to display alongside the forecast
3. Toggle the **confidence band** (±10% heuristic) on or off
4. Expand **View Raw Forecast Data** to download hourly predictions as a table

### Model Comparison
Side-by-side evaluation of all three models:
- **Metrics table** — MAE, RMSE, R² and inference speed at a glance
- **Bar charts** — visual comparison across all three metrics
- **Predictions vs Actuals** — first 200 test hours plotted for all models
- **Analysis** — plain-English explanation of why each model performed as it did

## 🧠 Key Technical Decisions
- **Temporal train/test split** — never random split time series data
- **Lag features** (1h, 24h, 168h) — the strongest predictors for autocorrelated series
- **Rolling forecast** for ARIMA — mirrors real production usage
- **Time interpolation** for missing values — preserves temporal continuity

## 📦 Tech Stack
`pandas` `numpy` `scikit-learn` `xgboost` `prophet` `statsmodels` `streamlit` `plotly`

## 📁 Dataset
UCI Household Power Consumption — 2,075,259 measurements over 4 years
at 1-minute intervals, resampled to hourly for this project.
