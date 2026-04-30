"""
Script to insert Seoul Bike Data into the database.
Loads CSV file and populates all tables with aggregated data using SQL.
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dashboard.database.db_connection import DatabaseConnection


def insert_bike_data(csv_path: str, db_path: str = "bikes.db"):
    """
    Load data from CSV and insert into all database tables.
    
    Args:
        csv_path (str): Path to the Seoul Bike Data CSV file
        db_path (str): Path to the SQLite database file
    """
    db = DatabaseConnection(db_path)
    
    print("\n" + "="*80)
    print("INSERTING DATA INTO DATABASE")
    print("="*80)
    
    # Load CSV data
    print("\nLoading CSV file...")
    df = pd.read_csv(csv_path, encoding='latin-1')
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    print(f"✓ Loaded {len(df)} records from CSV")
    
    # ============================================================
    # 1. INSERT INTO STAGING TABLE
    # ============================================================
    print("\n[1/5] Inserting data into stg_bike_rentals_hourly...")
    stg_data = []
    for _, row in df.iterrows():
        stg_data.append({
            "date": row['Date'].strftime('%Y-%m-%d'),
            "hour": int(row['Hour']),
            "rented_bike_count": int(row['Rented Bike Count']),
            "temperature": float(row['Temperature(°C)']),
            "humidity": int(row['Humidity(%)']),
            "wind_speed": float(row['Wind speed (m/s)']),
            "visibility": int(row['Visibility (10m)']),
            "dew_point_temperature": float(row['Dew point temperature(°C)']),
            "solar_radiation": float(row['Solar Radiation (MJ/m2)']),
            "rainfall": float(row['Rainfall(mm)']),
            "snowfall": float(row['Snowfall (cm)']),
            "seasons": row['Seasons'],
            "holiday": row['Holiday'],
            "functioning_day": row['Functioning Day']
        })
    
    if db.insert_many("stg_bike_rentals_hourly", stg_data):
        print(f"✓ Inserted {len(stg_data)} records into stg_bike_rentals_hourly")
    
    # # ============================================================
    # # 2. INSERT INTO DAILY FACT TABLE USING SQL
    # # ============================================================
    # print("\n[2/5] Inserting data into fact_bike_rentals_daily using SQL...")
    # sql_daily = """
    # INSERT INTO fact_bike_rentals_daily (date, total_bike_count, avg_bike_count, max_bike_count, min_bike_count)
    # SELECT 
    #     date,
    #     SUM(rented_bike_count) as total_bike_count,
    #     ROUND(AVG(rented_bike_count), 2) as avg_bike_count,
    #     MAX(rented_bike_count) as max_bike_count,
    #     MIN(rented_bike_count) as min_bike_count
    # FROM stg_bike_rentals_hourly
    # GROUP BY date
    # """
    
    # if db.execute_update(sql_daily):
    #     count = db.execute_query("SELECT COUNT(*) FROM fact_bike_rentals_daily")
    #     if count:
    #         print(f"✓ Inserted {count[0][0]} records into fact_bike_rentals_daily")
    
    # # ============================================================
    # # 3. INSERT INTO WEEKLY FACT TABLE USING SQL
    # # ============================================================
    # print("\n[3/5] Inserting data into fact_bike_rentals_weekly using SQL...")
    # sql_weekly = """
    # INSERT INTO fact_bike_rentals_weekly (year, week, start_date, end_date, total_bike_count, avg_bike_count, max_bike_count, min_bike_count)
    # SELECT 
    #     CAST(strftime('%Y', date) AS INTEGER) as year,
    #     CAST(strftime('%W', date) AS INTEGER) as week,
    #     MIN(date) as start_date,
    #     MAX(date) as end_date,
    #     SUM(rented_bike_count) as total_bike_count,
    #     ROUND(AVG(rented_bike_count), 2) as avg_bike_count,
    #     MAX(rented_bike_count) as max_bike_count,
    #     MIN(rented_bike_count) as min_bike_count
    # FROM stg_bike_rentals_hourly
    # GROUP BY year, week
    # ORDER BY year, week
    # """
    
    # if db.execute_update(sql_weekly):
    #     count = db.execute_query("SELECT COUNT(*) FROM fact_bike_rentals_weekly")
    #     if count:
    #         print(f"✓ Inserted {count[0][0]} records into fact_bike_rentals_weekly")
    
    # # ============================================================
    # # 4. INSERT INTO MONTHLY FACT TABLE USING SQL
    # # ============================================================
    # print("\n[4/5] Inserting data into fact_bike_rentals_monthly using SQL...")
    # sql_monthly = """
    # INSERT INTO fact_bike_rentals_monthly (year, month, month_name, total_bike_count, avg_bike_count, max_bike_count, min_bike_count)
    # SELECT 
    #     CAST(strftime('%Y', date) AS INTEGER) as year,
    #     CAST(strftime('%m', date) AS INTEGER) as month,
    #     CASE CAST(strftime('%m', date) AS INTEGER)
    #         WHEN 1 THEN 'January'
    #         WHEN 2 THEN 'February'
    #         WHEN 3 THEN 'March'
    #         WHEN 4 THEN 'April'
    #         WHEN 5 THEN 'May'
    #         WHEN 6 THEN 'June'
    #         WHEN 7 THEN 'July'
    #         WHEN 8 THEN 'August'
    #         WHEN 9 THEN 'September'
    #         WHEN 10 THEN 'October'
    #         WHEN 11 THEN 'November'
    #         WHEN 12 THEN 'December'
    #     END as month_name,
    #     SUM(rented_bike_count) as total_bike_count,
    #     ROUND(AVG(rented_bike_count), 2) as avg_bike_count,
    #     MAX(rented_bike_count) as max_bike_count,
    #     MIN(rented_bike_count) as min_bike_count
    # FROM stg_bike_rentals_hourly
    # GROUP BY year, month
    # ORDER BY year, month
    # """
    
    # if db.execute_update(sql_monthly):
    #     count = db.execute_query("SELECT COUNT(*) FROM fact_bike_rentals_monthly")
    #     if count:
    #         print(f"✓ Inserted {count[0][0]} records into fact_bike_rentals_monthly")
    
    # # ============================================================
    # # 5. INSERT INTO ANNUAL FACT TABLE USING SQL
    # # ============================================================
    # print("\n[5/5] Inserting data into fact_bike_rentals_annual using SQL...")
    # sql_annual = """
    # INSERT INTO fact_bike_rentals_annual (year, total_bike_count, avg_bike_count, max_bike_count, min_bike_count, total_days)
    # SELECT 
    #     CAST(strftime('%Y', date) AS INTEGER) as year,
    #     SUM(rented_bike_count) as total_bike_count,
    #     ROUND(AVG(rented_bike_count), 2) as avg_bike_count,
    #     MAX(rented_bike_count) as max_bike_count,
    #     MIN(rented_bike_count) as min_bike_count,
    #     COUNT(DISTINCT date) as total_days
    # FROM stg_bike_rentals_hourly
    # GROUP BY year
    # ORDER BY year
    # """
    
    # if db.execute_update(sql_annual):
    #     count = db.execute_query("SELECT COUNT(*) FROM fact_bike_rentals_annual")
    #     if count:
    #         print(f"✓ Inserted {count[0][0]} records into fact_bike_rentals_annual")
    
    # # Display summary
    # print("\n" + "="*80)
    # print("DATA INSERTION COMPLETE")
    # print("="*80)
    
    # tables = [
    #     "stg_bike_rentals_hourly",
    #     "fact_bike_rentals_daily",
    #     "fact_bike_rentals_weekly",
    #     "fact_bike_rentals_monthly",
    #     "fact_bike_rentals_annual"
    # ]
    
    # for table in tables:
    #     count = db.execute_query(f"SELECT COUNT(*) FROM {table}")
    #     if count:
    #         print(f"✓ {table:<30s}: {count[0][0]:>6} records")
    
    # db.close()
    # print("="*80)
    # print("All data inserted successfully!")
    # print("="*80)


if __name__ == "__main__":
    # Get the paths
    current_dir = Path(__file__).parent
    csv_path = current_dir.parent / "data" / "SeoulBikeData.csv"
    db_path = current_dir / "database" / "bikes.db"
    
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        sys.exit(1)
    
    print(f"CSV file: {csv_path}")
    print(f"Database: {db_path}")
    
    insert_bike_data(str(csv_path), str(db_path))
