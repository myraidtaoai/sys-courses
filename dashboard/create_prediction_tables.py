"""
Script to create prediction tables in the database
Stores 24-hour and 3-day ahead predictions
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dashboard.database.db_connection import DatabaseConnection


def create_prediction_tables(db_path: str = "bikes.db"):
    """
    Create tables for storing predictions
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    db = DatabaseConnection(db_path)
    
    print("\n" + "="*80)
    print("CREATING PREDICTION TABLES")
    print("="*80)
    
    # Drop existing tables to ensure clean schema
    print("Dropping existing prediction tables...")
    db.cursor.execute("DROP TABLE IF EXISTS pred_bike_rentals_24h")
    db.cursor.execute("DROP TABLE IF EXISTS pred_bike_rentals_3d")
    db.connection.commit()
    
    # ============================================================
    # 1. CREATE 24-HOUR PREDICTION TABLE
    # ============================================================
    print("\n[1/2] Creating pred_bike_rentals_24h table...")
    pred_24h_columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "selected_datetime": "DATETIME NOT NULL",
        "selected_date": "DATE NOT NULL",
        "selected_hour": "INTEGER NOT NULL",
        "prediction_datetime": "DATETIME NOT NULL",
        "prediction_date": "DATE NOT NULL",
        "prediction_hour": "INTEGER NOT NULL",
        "predicted_bikes": "REAL NOT NULL",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    
    if db.create_table("pred_bike_rentals_24h", pred_24h_columns):
        print("✓ pred_bike_rentals_24h created successfully")
    
    # ============================================================
    # 2. CREATE 3-DAY PREDICTION TABLE
    # ============================================================
    print("\n[2/2] Creating pred_bike_rentals_3d table...")
    pred_3d_columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "selected_datetime": "DATETIME NOT NULL",
        "selected_date": "DATE NOT NULL",
        "selected_hour": "INTEGER NOT NULL",
        "prediction_datetime": "DATETIME NOT NULL",
        "prediction_date": "DATE NOT NULL",
        "prediction_hour": "INTEGER NOT NULL",
        "predicted_bikes": "REAL NOT NULL",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    
    if db.create_table("pred_bike_rentals_3d", pred_3d_columns):
        print("✓ pred_bike_rentals_3d created successfully")
    
    # Display summary
    print("\n" + "="*80)
    print("PREDICTION TABLES CREATION COMPLETE")
    print("="*80)
    
    tables = ["pred_bike_rentals_24h", "pred_bike_rentals_3d"]
    
    for table in tables:
        info = db.get_table_info(table)
        if info:
            print(f"✓ {table:<30s}: {len(info)} columns")
    
    db.close()
    print("="*80)
    print("All prediction tables created successfully!")
    print("="*80)


if __name__ == "__main__":
    # Get database path
    current_dir = Path(__file__).parent
    db_path = current_dir / "database" / "bikes.db"
    
    print(f"Database path: {db_path}")
    
    create_prediction_tables(str(db_path))
