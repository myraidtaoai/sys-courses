import sqlite3
from typing import Dict, Any, List, Tuple, Optional

class LocalDatabaseManager:
    def __init__(self, db_name: str = "local_health.db"):
        """
        Initialize the database manager.
        In SQLite, connecting to a non-existent file creates the database automatically.
        """
        self.db_name = db_name

    def _get_connection(self) -> sqlite3.Connection:
        """Create a database connection to the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_name)
            # Enable accessing columns by name (row['column_name'])
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def create_table(self, table_name: str, columns: Dict[str, str]):
        """
        Create a table with given definition.
        columns: dict where key is column name and value is SQL type/constraints
        Example: {"id": "INTEGER PRIMARY KEY AUTOINCREMENT", "name": "TEXT NOT NULL"}
        """
        cols_def = ", ".join([f"{name} {definition}" for name, definition in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_def})"
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                print(f"Table '{table_name}' created successfully (or already exists).")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            raise

    def insert_record(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        Insert a single record into table.
        data: dict of column: value
        Returns: The ID of the inserted row (lastrowid).
        """
        columns = ", ".join(data.keys())
        # SQLite uses ? as placeholder
        placeholders = ", ".join(["?" for _ in data.keys()])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        values = list(data.values())
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, values)
                conn.commit()
                print(f"Record inserted into '{table_name}'. ID: {cursor.lastrowid}")
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting record: {e}")
            raise

    def update_record(self, table_name: str, data: Dict[str, Any], where_clause: str, where_params: Tuple) -> int:
        """
        Update records in table.
        data: dict of column: value to update
        where_clause: SQL condition (e.g., "id = ?")
        where_params: tuple of parameters for the where clause
        Returns: Number of rows affected.
        """
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        values = list(data.values()) + list(where_params)
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, values)
                conn.commit()
                print(f"Updated {cursor.rowcount} record(s) in '{table_name}'.")
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error updating record: {e}")
            raise

    def delete_record(self, table_name: str, where_clause: str, where_params: Tuple) -> int:
        """
        Delete records from table.
        where_clause: SQL condition (e.g., "id = ?")
        where_params: tuple of parameters for the where clause
        Returns: Number of rows deleted.
        """
        sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, where_params)
                conn.commit()
                print(f"Deleted {cursor.rowcount} record(s) from '{table_name}'.")
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error deleting record: {e}")
            raise

    def fetch_all(self, table_name: str, where_clause: str = None, where_params: Tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all records matching the condition as a list of dictionaries."""
        sql = f"SELECT * FROM {table_name}"
        if where_clause:
            sql += f" WHERE {where_clause}"
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, where_params)
            return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close the database connection."""
        # In this implementation, connections are managed with context managers,
        # so there's no persistent connection to close.
        pass