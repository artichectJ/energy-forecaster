import pandas as pd
import numpy as np


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineers time-based and lag features from the cleaned DataFrame.
    These features are what give our models the context to learn patterns.

    Args:
        df: Clean DataFrame from data_loader.py

    Returns:
        DataFrame enriched with additional features.
    """

    print("⚙️  Engineering features...")
    df = df.copy()

    # --- Time-based features ---
    df["hour"]        = df.index.hour
    df["day_of_week"] = df.index.dayofweek      # 0 = Monday, 6 = Sunday
    df["month"]       = df.index.month
    df["quarter"]     = df.index.quarter
    df["year"]        = df.index.year
    df["is_weekend"]  = df["day_of_week"].isin([5, 6]).astype(int)
    df["is_night"]    = df["hour"].between(22, 6).astype(int)

    # --- Season feature ---
    df["season"] = df["month"].map({
        12: "Winter", 1: "Winter", 2: "Winter",
        3:  "Spring", 4: "Spring", 5: "Spring",
        6:  "Summer", 7: "Summer", 8: "Summer",
        9:  "Autumn", 10: "Autumn", 11: "Autumn",
    })
    df["season_code"] = df["season"].map(
        {"Winter": 0, "Spring": 1, "Summer": 2, "Autumn": 3}
    )

    # --- Lag features (past values as predictors) ---
    df["lag_1h"]  = df["active_power"].shift(1)   # 1 hour ago
    df["lag_24h"] = df["active_power"].shift(24)  # same hour yesterday
    df["lag_168h"] = df["active_power"].shift(168) # same hour last week

    # --- Rolling window features ---
    df["rolling_mean_24h"] = (
        df["active_power"].rolling(window=24, min_periods=1).mean()
    )
    df["rolling_std_24h"] = (
        df["active_power"].rolling(window=24, min_periods=1).std()
    )
    df["rolling_mean_168h"] = (
        df["active_power"].rolling(window=168, min_periods=1).mean()
    )

    # Drop rows with NaN from lag features
    df.dropna(inplace=True)

    print(f"✅ Features engineered! Dataset shape: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")
    return df


if __name__ == "__main__":
    from data_loader import load_data

    df_clean = load_data(resample_freq="h")
    df_featured = engineer_features(df_clean)

    print("\nFirst 3 rows with new features:")
    print(df_featured.head(3).to_string())