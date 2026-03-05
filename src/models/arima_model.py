import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = ROOT_DIR / "data" / "models"
MODELS_DIR.mkdir(exist_ok=True)

TARGET_COL = "active_power"


def check_stationarity(series: pd.Series) -> bool:
    """
    Runs the Augmented Dickey-Fuller test to check if the series is stationary.
    ARIMA requires stationary data — i.e. constant mean and variance over time.

    Returns True if stationary, False if not.
    """
    result = adfuller(series.dropna())
    p_value = result[1]
    is_stationary = p_value < 0.05
    print(f"📉 ADF Test p-value: {p_value:.6f} → "
          f"{'Stationary ✅' if is_stationary else 'Non-stationary ❌'}")
    return is_stationary


def train_test_split_temporal(
    df: pd.DataFrame, test_size: float = 0.2
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Temporal split — never random split time series data."""
    split_idx = int(len(df) * (1 - test_size))
    return df.iloc[:split_idx], df.iloc[split_idx:]


def evaluate(y_true: pd.Series, y_pred: np.ndarray) -> dict:
    """Returns a dictionary of evaluation metrics."""
    return {
        "MAE":  round(mean_absolute_error(y_true, y_pred), 4),
        "RMSE": round(np.sqrt(mean_squared_error(y_true, y_pred)), 4),
        "R2":   round(r2_score(y_true, y_pred), 4),
    }


def train(df: pd.DataFrame) -> tuple[object, dict, pd.DataFrame]:
    """
    Trains an ARIMA model using a rolling forecast strategy.

    ARIMA order (p, d, q):
      p = 24  → uses last 24 hours of data (autoregressive)
      d = 0   → no differencing needed (data is stationary)
      q = 2   → uses last 2 forecast errors (moving average)

    Returns:
        model:   Fitted ARIMA model on full training data
        metrics: MAE, RMSE, R2 on the test set
        test_df: Test portion with predictions attached
    """
    series = df[TARGET_COL]
    train_df, test_df = train_test_split_temporal(df)

    train_series = train_df[TARGET_COL]
    test_series  = test_df[TARGET_COL]

    # Check stationarity
    check_stationarity(train_series)

    # Use last 2000 rows for training, only forecast 200 steps
    # ARIMA is O(n²) — forecasting thousands of steps is not practical
    train_subset = train_series.iloc[-2000:]
    test_subset  = test_series.iloc[:200]

    print(f"🔢 Training ARIMA on {len(train_subset):,} rows...")
    print(f"📋 Forecasting {len(test_subset):,} steps ahead...")
    print("⏳ Estimated time: 3–5 minutes on M3...")

    history     = list(train_subset)
    predictions = []
    step        = 0

    for t in range(len(test_subset)):
        model = ARIMA(history, order=(24, 0, 2))
        fit   = model.fit()
        yhat  = fit.forecast(steps=1)[0]
        predictions.append(yhat)
        history.append(test_subset.iloc[t])

        step += 1
        if step % 50 == 0:
            print(f"   → Forecasted {step}/{len(test_subset)} steps...")

    predictions = np.clip(np.array(predictions), 0, None)
    metrics     = evaluate(test_subset, predictions)

    result_df = test_df.copy()
    # Attach predictions only to the subset we forecasted
    result_df["predicted"] = np.nan
    result_df.iloc[:200, result_df.columns.get_loc("predicted")] = predictions

    # Save the final model
    final_model = ARIMA(train_series.iloc[-2000:], order=(24, 0, 2)).fit()
    model_path  = MODELS_DIR / "arima_model.pkl"
    joblib.dump(final_model, model_path)
    print(f"💾 Model saved to {model_path}")

    print(f"\n📊 ARIMA Test Metrics:")
    for k, v in metrics.items():
        print(f"   {k}: {v}")

    return final_model, metrics, result_df


if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from data_loader import load_data
    from features import engineer_features

    df = load_data(resample_freq="h")
    df = engineer_features(df)
    model, metrics, test_df = train(df)

    print("\nSample predictions vs actuals:")
    print(test_df[["active_power", "predicted"]].head(10).to_string())