import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from pathlib import Path
import logging

# Suppress Prophet's verbose Stan output
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = ROOT_DIR / "data" / "models"
MODELS_DIR.mkdir(exist_ok=True)

TARGET_COL = "active_power"


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


def train(df: pd.DataFrame) -> tuple[Prophet, dict, pd.DataFrame]:
    """
    Trains a Prophet model on the featured DataFrame.
    Prophet expects columns named exactly 'ds' (datetime) and 'y' (target).

    Returns:
        model:   Trained Prophet model
        metrics: MAE, RMSE, R2 on the test set
        test_df: Test portion with predictions attached
    """
    # Prophet requires specific column names
    prophet_df = df[[TARGET_COL]].reset_index()
    prophet_df.columns = ["ds", "y"]

    # Add regressors — extra features Prophet can use
    prophet_df["hour"]             = df["hour"].values
    prophet_df["is_weekend"]       = df["is_weekend"].values
    prophet_df["rolling_mean_24h"] = df["rolling_mean_24h"].values
    prophet_df["lag_24h"]          = df["lag_24h"].values

    split_idx = int(len(prophet_df) * 0.8)
    train_df  = prophet_df.iloc[:split_idx]
    test_df   = prophet_df.iloc[split_idx:]

    print("🔮 Training Prophet model...")
    model = Prophet(
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=10,
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
    )

    # Add extra regressors
    model.add_regressor("hour")
    model.add_regressor("is_weekend")
    model.add_regressor("rolling_mean_24h")
    model.add_regressor("lag_24h")

    model.fit(train_df)

    # Predict on test set
    forecast = model.predict(test_df)
    preds     = forecast["yhat"].values
    y_test    = test_df["y"].values

    # Clip negative predictions (energy can't be negative)
    preds = np.clip(preds, 0, None)

    metrics = evaluate(y_test, preds)

    result_df = test_df.copy()
    result_df["predicted"] = preds
    result_df = result_df.set_index("ds")

    # Save model
    model_path = MODELS_DIR / "prophet_model.pkl"
    joblib.dump(model, model_path)
    print(f"💾 Model saved to {model_path}")

    print(f"\n📊 Prophet Test Metrics:")
    for k, v in metrics.items():
        print(f"   {k}: {v}")

    return model, metrics, result_df


if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from data_loader import load_data
    from features import engineer_features

    df = load_data(resample_freq="h")
    df = engineer_features(df)
    model, metrics, test_df = train(df)

    print("\nSample predictions vs actuals:")
    print(test_df[["y", "predicted"]].head(10).to_string())