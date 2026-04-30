import datetime
import sqlite3
import pandas as pd
import sys
import os
from pathlib import Path
import warnings
from pathlib import Path
from darts import TimeSeries, concatenate
from darts.models import LinearRegressionModel
from database.db_connection import DatabaseConnection

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# ==========================================
# CONFIGURATION
# ==========================================
# Get database path
# Add the parent directory to sys.path so 'dashboard' can be imported if it's a local package
current_dir = Path(os.getcwd())
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
	sys.path.insert(0, str(parent_dir))
DB_PATH = current_dir / "database" / "bikes.db"

# Model Paths (Adjust if necessary)
MODEL_24H_PATH = "../models/linear_24h_model.pkl"
MODEL_3D_PATH = "../models/linear_3d_model.pkl" 

Selected_Date_Start= "2018-11-20"
Selected_Date_END = "2018-11-30"
# ==========================================

class DatabaseConnection:
    """Wrapper for SQLite database connection."""
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        self._connect()

    def _connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def insert_data(self, table_name, data):
        """Inserts a list of dictionaries into the table."""
        if not data:
            return
        
        columns = ", ".join(data[0].keys())
        placeholders = ", ".join(["?" for _ in data[0].keys()])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        values = [tuple(row.values()) for row in data]
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, values)
            self.connection.commit()
            print(f"Successfully inserted {len(data)} rows into {table_name}")
        except sqlite3.Error as e:
            print(f"Error inserting data into {table_name}: {e}")

    def get_stg_data(self):
        """Fetches all data from the staging table."""
        query = "SELECT * FROM stg_bike_rentals_hourly ORDER BY date, hour"
        try:
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            print(f"Error reading from stg_bike_rentals_hourly: {e}")
            return None

    def close(self):
        if self.connection:
            self.connection.close()

def preprocess_data(df):
    """
    Transforms the database dataframe into the format required by the model.
    """
    print("Preprocessing data from database...")
    
    # 1. Create Datetime Column
    df['datetime'] = pd.to_datetime(df['date'].astype(str) + ' ' + df['hour'].astype(str) + ':00:00')
    
    # --- FIX START: Remove Duplicates ---
    # We check for duplicate timestamps and keep the first occurrence.
    initial_count = len(df)
    df = df.drop_duplicates(subset=['datetime'], keep='first')
    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        print(f"Warning: Dropped {dropped_count} duplicate rows found in database.")
    # --- FIX END ---

    # 2. Set Index
    df.set_index('datetime', inplace=True)
    df = df.sort_index()

    # 3. Rename columns if necessary
    if 'rented_bike_count' in df.columns:
        df.rename(columns={'rented_bike_count': 'hourly_count'}, inplace=True)

    # 4. Feature Engineering
    numerical_features = [
        'hourly_count', 'temperature', 'humidity', 'wind_speed', 'visibility',
        'dew_point_temperature', 'solar_radiation', 'rainfall', 'snowfall'
    ]
    
    # Handle potential column name mismatches (e.g. typos in source data)
    available_cols = df.columns.tolist()
    final_numerical = [c for c in numerical_features if c in available_cols]
    
    categorical_cols = ['seasons', 'holiday', 'functioning_day']
   
    
    # Create Dummies
    df_categorical = df[categorical_cols]
    df_dummies = pd.get_dummies(df_categorical)
    df_dummies = df_dummies.replace({False: 0, True: 1})
    
    # Merge
    df_processed = pd.merge(df[final_numerical], df_dummies, left_index=True, right_index=True)
    ROR:darts.timeseries:IndexError: Integer index out of range.
    return df_processed

def generate_predictions(hist_df, all_df, model_path, horizon_hours):
    """Loads a model and generates historical forecasts."""
    print(f"\n--- Processing {horizon_hours}-hour Prediction ---")
    
    if not Path(model_path).exists():
        print(f"Error: Model file not found at {model_path}")
        return None

    print(f"Loading model from {model_path}...")
    try:
        model = LinearRegressionModel.load(model_path)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return None

    print("Preparing TimeSeries data...")
    # Target series
    ts_series = TimeSeries.from_dataframe(hist_df[['hourly_count']], freq='h')
    
    # Covariates series (all other columns)
    features_df = all_df.drop(['hourly_count'], axis=1)
    features_series = TimeSeries.from_dataframe(features_df, freq='h')
    
    try:
        predictions = model.predict(
            n=horizon_hours,
            series=ts_series,
            future_covariates=features_series,
            verbose=False
        )
        return predictions

    except Exception as e:
        print(f"Prediction failed: {e}")
        return None


def prepare_db_records(predictions, selected_time):
    """Converts Darts TimeSeries predictions into database record format."""
    records = []
    if not predictions:
        return []

    # Use ignore_time_axis=True to concatenate potentially non-contiguous or overlapping series
    predictions = concatenate(predictions, ignore_time_axis=True)
    df_pred = predictions.to_dataframe()
    
    for pred_time, row in df_pred.iterrows():
        # Clip negative predictions to 0
        predicted_val = max(0, row.iloc[0])
        
        record = {
            "selected_datetime": selected_time.strftime("%Y-%m-%d %H:%M:%S"),
            "selected_date": selected_time.strftime("%Y-%m-%d"),
            "selected_hour": int(selected_time.hour),
            "prediction_datetime": pred_time.strftime("%Y-%m-%d %H:%M:%S"),
            "prediction_date": pred_time.strftime("%Y-%m-%d"),
            "prediction_hour": int(pred_time.hour),
            "predicted_bikes": float(predicted_val)
        }
        records.append(record)
        
    return records

def main():
    print("Starting hourly predictions process...\n")
    # 1. Create the range of datetime for which predictions are to be made
    datetime_range = pd.date_range(start=Selected_Date_Start, end=Selected_Date_END, freq='H')

    # 2. Initialize DB Connection
    db = DatabaseConnection(DB_PATH)

    # 3. Load Data from DB
    print(f"Fetching data from {DB_PATH}...")
    df_raw = db.get_stg_data()
    
    if df_raw is None or df_raw.empty:
        print("No data found in stg_bike_rentals_hourly.")
        db.close()
        return

    # 4. Preprocess Data
    df_processed = preprocess_data(df_raw)

    # 5. Predict & Insert (24 Hours)
    for selected_time in datetime_range:
        print(f"Generating 24-hour forecasts at {selected_time} ...")
        hist_df_processed = df_processed[df_processed.index <= selected_time]
        preds_24h = generate_predictions(hist_df_processed, df_processed, MODEL_24H_PATH, 24)
        if preds_24h:
            records_24h = prepare_db_records(preds_24h, selected_time)
            print(f"Inserting {len(records_24h)} records into pred_bike_rentals_24h for selected time {selected_time}...")
            db.insert_data("pred_bike_rentals_24h", records_24h)

    # 6. Predict & Insert (3 Days / 72 Hours)
    for selected_time in datetime_range:
        print(f"Generating 3-day forecasts at {selected_time} ...")
        hist_df_processed = df_processed[df_processed.index <= selected_time]
        preds_3d = generate_predictions(hist_df_processed, df_processed, MODEL_3D_PATH, 72)
        if preds_3d:
            records_3d = prepare_db_records(preds_3d, selected_time)
            print(f"Inserting {len(records_3d)} records into pred_bike_rentals_3d for selected time {selected_time}...")
            db.insert_data("pred_bike_rentals_3d", records_3d)

    db.close()
    print("\nProcessing complete.")

if __name__ == "__main__":
    main()