
import sys
from pathlib import Path
sys.path.insert(0, ".")
from dashboard.database.db_connection import DatabaseConnection

db = DatabaseConnection('dashboard/database/bikes.db')
res = db.execute_query("SELECT MIN(date), MAX(date) FROM stg_bike_rentals_hourly")
print(f"Date range: {res}")
db.close()
