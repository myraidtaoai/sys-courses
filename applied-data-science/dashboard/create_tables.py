"""
Script to create database tables with standard data warehouse naming conventions.
This script creates the schema without inserting any data.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dashboard.database.db_connection import DatabaseConnection


def create_database_schema(db_path: str = "bikes.db"):
    """
    Create all required tables in the database.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    db = DatabaseConnection(db_path)
    
    print("\n" + "="*80)
    print("CREATING DATABASE SCHEMA")
    print("="*80)
    
    # ============================================================
    # 1. CREATE STAGING TABLE - HOURLY DATA
    # ============================================================
    print("\n[1/5] Creating stg_bike_rentals_hourly table...")
    stg_columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "date": "DATE NOT NULL",
        "hour": "INTEGER NOT NULL",
        "rented_bike_count": "INTEGER NOT NULL",
        "temperature": "REAL",
        "humidity": "INTEGER",
        "wind_speed": "REAL",
        "visibility": "INTEGER",
        "dew_point_temperature": "REAL",
        "solar_radiation": "REAL",
        "rainfall": "REAL",
        "snowfall": "REAL",
        "seasons": "TEXT",
        "holiday": "TEXT",
        "functioning_day": "TEXT"
    }
    
    if db.create_table("stg_bike_rentals_hourly", stg_columns):
        print("✓ stg_bike_rentals_hourly created successfully")
    
    # ============================================================
    # 2. CREATE FACT TABLE - DAILY AGGREGATION
    # ============================================================
    print("\n[2/5] Creating fact_bike_rentals_daily table...")
    daily_columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "date": "STRING NOT NULL",
        "total_bike_count": "INTEGER NOT NULL",
        "avg_bike_count": "REAL",
        "max_bike_count": "INTEGER",
        "min_bike_count": "INTEGER"
    }
    
    if db.create_table("fact_bike_rentals_daily", daily_columns):
        print("✓ fact_bike_rentals_daily created successfully")
    
    # ============================================================
    # 3. CREATE FACT TABLE - WEEKLY AGGREGATION
    # ============================================================
    print("\n[3/5] Creating fact_bike_rentals_weekly table...")
    weekly_columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "year": "INTEGER NOT NULL",
        "week": "INTEGER NOT NULL",
        "start_date": "DATE NOT NULL",
        "end_date": "DATE NOT NULL",
        "total_bike_count": "INTEGER NOT NULL",
        "avg_bike_count": "REAL",
        "max_bike_count": "INTEGER",
        "min_bike_count": "INTEGER"
    }
    
    if db.create_table("fact_bike_rentals_weekly", weekly_columns):
        print("✓ fact_bike_rentals_weekly created successfully")
    
    # ============================================================
    # 4. CREATE FACT TABLE - MONTHLY AGGREGATION
    # ============================================================
    print("\n[4/5] Creating fact_bike_rentals_monthly table...")
    monthly_columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "year": "INTEGER NOT NULL",
        "month": "INTEGER NOT NULL",
        "month_name": "TEXT NOT NULL",
        "total_bike_count": "INTEGER NOT NULL",
        "avg_bike_count": "REAL",
        "max_bike_count": "INTEGER",
        "min_bike_count": "INTEGER"
    }
    
    if db.create_table("fact_bike_rentals_monthly", monthly_columns):
        print("✓ fact_bike_rentals_monthly created successfully")
    
    # ============================================================
    # 5. CREATE FACT TABLE - ANNUAL AGGREGATION
    # ============================================================
    print("\n[5/5] Creating fact_bike_rentals_annual table...")
    annual_columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "year": "INTEGER UNIQUE NOT NULL",
        "total_bike_count": "INTEGER NOT NULL",
        "avg_bike_count": "REAL",
        "max_bike_count": "INTEGER",
        "min_bike_count": "INTEGER",
        "total_days": "INTEGER"
    }
    
    if db.create_table("fact_bike_rentals_annual", annual_columns):
        print("✓ fact_bike_rentals_annual created successfully")
    
    # Display summary
    print("\n" + "="*80)
    print("SCHEMA CREATION COMPLETE")
    print("="*80)
    
    tables = [
        "stg_bike_rentals_hourly",
        "fact_bike_rentals_daily",
        "fact_bike_rentals_weekly",
        "fact_bike_rentals_monthly",
        "fact_bike_rentals_annual"
    ]
    
    for table in tables:
        info = db.get_table_info(table)
        if info:
            print(f"✓ {table:<30s}: {len(info)} columns")
    
    db.close()
    print("="*80)
    print("All tables created successfully!")
    print("="*80)


if __name__ == "__main__":
    import os
    
    # Get database path
    current_dir = Path(__file__).parent
    db_path = current_dir / "database" / "bikes.db"
    
    print(f"Database path: {db_path}")
    
    create_database_schema(str(db_path))
