import pandas as pd
import numpy as np
from pathlib import Path

# Project root and data path
ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = ROOT_DIR / "data" / "raw" / "household_power_consumption.txt"


def load_data(resample_freq: str = "h") -> pd.DataFrame:
    """
    Loads, cleans and resamples the UCI Household Power Consumption dataset.

    Args:
        resample_freq: Resampling frequency — 'H' for hourly, 'D' for daily.

    Returns:
        A clean, indexed, resampled DataFrame ready for EDA and modelling.
    """

    print("📂 Loading raw data...")
    df = pd.read_csv(
        RAW_DATA_PATH,
        sep=";",
        low_memory=False,
        na_values=["?"],
    )

    print("🧹 Cleaning and parsing timestamps...")
    # Merge Date and Time into a single datetime index
    df["datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"], format="%d/%m/%Y %H:%M:%S"
    )
    df.drop(columns=["Date", "Time"], inplace=True)
    df.set_index("datetime", inplace=True)

    # Cast all columns to numeric (they come in as strings)
    df = df.apply(pd.to_numeric, errors="coerce")

    print(f"🔍 Missing values before cleaning: {df.isnull().sum().sum():,}")

    # Interpolate missing values (better than dropping for time-series)
    df.interpolate(method="time", inplace=True)

    print(f"✅ Missing values after cleaning: {df.isnull().sum().sum():,}")

    # Rename columns to something readable
    df.rename(columns={
        "Global_active_power":   "active_power",
        "Global_reactive_power": "reactive_power",
        "Voltage":               "voltage",
        "Global_intensity":      "intensity",
        "Sub_metering_1":        "kitchen",
        "Sub_metering_2":        "laundry",
        "Sub_metering_3":        "hvac",
    }, inplace=True)

    print(f"📊 Resampling to frequency: '{resample_freq}'...")
    df = df.resample(resample_freq).mean()

    print(f"🎉 Done! Dataset shape: {df.shape}")
    return df


if __name__ == "__main__":
    df = load_data(resample_freq="h")
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nData types:")
    print(df.dtypes)
    print("\nBasic stats:")
    print(df.describe())