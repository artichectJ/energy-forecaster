import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = ROOT_DIR / "data" / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Features the model will train on
FEATURE_COLS = [
    "hour", "day_of_week", "month", "quarter", "season_code",
    "is_weekend", "is_night", "lag_1h", "lag_24h", "lag_168h",
    "rolling_mean_24h", "rolling_std_24h", "rolling_mean_168h",
    "voltage", "intensity"
]
TARGET_COL = "active_power"


def train_test_split_temporal(
    df: pd.DataFrame, test_size: float = 0.2
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits data temporally — last 20% of time is test set.
    We never random-split time series data as it causes data leakage.
    """
    split_idx = int(len(df) * (1 - test_size))
    return df.iloc[:split_idx], df.iloc[split_idx:]


def evaluate(y_true: pd.Series, y_pred: np.ndarray) -> dict:
    """Returns a dictionary of evaluation metrics."""
    return {
        "MAE":  round(mean_absolute_error(y_true, y_pred), 4),
        "RMSE": round(np.sqrt(mean_squared_error(y_true, y_pred)), 4),
        "R2":   round(r2_score(y_true, y_pred), 4),
    }


def train(df: pd.DataFrame) -> tuple[XGBRegressor, dict, pd.DataFrame]:
    """
    Trains an XGBoost model on the featured DataFrame.

    Returns:
        model:   Trained XGBRegressor
        metrics: MAE, RMSE, R2 on the test set
        test_df: Test portion with predictions attached
    """
    train_df, test_df = train_test_split_temporal(df)

    X_train = train_df[FEATURE_COLS]
    y_train = train_df[TARGET_COL]
    X_test  = test_df[FEATURE_COLS]
    y_test  = test_df[TARGET_COL]

    print("🚀 Training XGBoost model...")
    model = XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=100,
    )

    preds = model.predict(X_test)
    metrics = evaluate(y_test, preds)

    test_df = test_df.copy()
    test_df["predicted"] = preds

    # Save model to disk
    model_path = MODELS_DIR / "xgboost_model.pkl"
    joblib.dump(model, model_path)
    print(f"💾 Model saved to {model_path}")

    print(f"\n📊 XGBoost Test Metrics:")
    for k, v in metrics.items():
        print(f"   {k}: {v}")

    return model, metrics, test_df


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