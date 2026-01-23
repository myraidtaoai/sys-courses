"""
DatabaseConnection class for managing local database operations.
Provides a simple interface for executing SQL queries to create and update tables.
"""

import sqlite3
from typing import Any, List, Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    A class to manage local SQLite database connections and operations.
    
    Attributes:
        db_path (str): Path to the SQLite database file
        connection: SQLite connection object
        cursor: SQLite cursor object
    """
    
    def __init__(self, db_path: str = "local_database.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path (str): Path to the SQLite database file. 
                          Defaults to "local_database.db" in the current directory.
        """
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self) -> None:
        """
        Establish a connection to the SQLite database.
        Creates the database file if it doesn't exist.
        """
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def commit(self) -> None:
        """Commit changes to the database."""
        self.connection.commit()
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.commit()
            self.connection.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = ()) -> Optional[List[tuple]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Query parameters for parameterized queries
            
        Returns:
            List[tuple]: Query results, or None if query fails
        """
        try:
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            logger.info(f"Query executed successfully")
            return results
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {e}")
            return None
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query (str): SQL query to execute
            params (tuple): Query parameters for parameterized queries
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            logger.info(f"Update executed successfully. Rows affected: {self.cursor.rowcount}")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error executing update: {e}")
            self.connection.rollback()
            return False
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """
        Create a new table in the database.
        
        Args:
            table_name (str): Name of the table to create
            columns (Dict[str, str]): Dictionary mapping column names to their SQL types
                                      Example: {"id": "INTEGER PRIMARY KEY", "name": "TEXT NOT NULL"}
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Build the CREATE TABLE statement
            columns_sql = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
            
            self.cursor.execute(query)
            self.connection.commit()
            logger.info(f"Table '{table_name}' created successfully")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error creating table: {e}")
            self.connection.rollback()
            return False
    
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """
        Insert a single row of data into a table.
        
        Args:
            table_name (str): Name of the table
            data (Dict[str, Any]): Dictionary mapping column names to values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data.values()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            self.cursor.execute(query, tuple(data.values()))
            self.connection.commit()
            logger.info(f"Data inserted into '{table_name}' successfully")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error inserting data: {e}")
            self.connection.rollback()
            return False
    
    def insert_many(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """
        Insert multiple rows of data into a table.
        
        Args:
            table_name (str): Name of the table
            data (List[Dict[str, Any]]): List of dictionaries, each representing a row
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not data:
            logger.warning("No data provided to insert")
            return False
        
        try:
            columns = ", ".join(data[0].keys())
            placeholders = ", ".join(["?" for _ in data[0].values()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            rows = [tuple(row.values()) for row in data]
            self.cursor.executemany(query, rows)
            self.connection.commit()
            logger.info(f"Inserted {len(data)} rows into '{table_name}' successfully")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error inserting multiple rows: {e}")
            self.connection.rollback()
            return False
    
    def update_data(self, table_name: str, set_columns: Dict[str, Any], 
                   where_clause: str = "", where_params: tuple = ()) -> bool:
        """
        Update existing data in a table.
        
        Args:
            table_name (str): Name of the table
            set_columns (Dict[str, Any]): Dictionary of columns to update with their new values
            where_clause (str): WHERE clause condition (without WHERE keyword)
            where_params (tuple): Parameters for the WHERE clause
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            set_sql = ", ".join([f"{col} = ?" for col in set_columns.keys()])
            query = f"UPDATE {table_name} SET {set_sql}"
            
            params = tuple(set_columns.values())
            if where_clause:
                query += f" WHERE {where_clause}"
                params = params + where_params
            
            self.cursor.execute(query, params)
            self.connection.commit()
            logger.info(f"Updated {self.cursor.rowcount} rows in '{table_name}'")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating data: {e}")
            self.connection.rollback()
            return False
    
    def delete_data(self, table_name: str, where_clause: str = "", 
                   where_params: tuple = ()) -> bool:
        """
        Delete rows from a table.
        
        Args:
            table_name (str): Name of the table
            where_clause (str): WHERE clause condition (without WHERE keyword)
            where_params (tuple): Parameters for the WHERE clause
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = f"DELETE FROM {table_name}"
            if where_clause:
                query += f" WHERE {where_clause}"
            
            self.cursor.execute(query, where_params)
            self.connection.commit()
            logger.info(f"Deleted {self.cursor.rowcount} rows from '{table_name}'")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error deleting data: {e}")
            self.connection.rollback()
            return False
    
    def get_table_info(self, table_name: str) -> Optional[List[tuple]]:
        """
        Get information about table columns.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            List[tuple]: Column information, or None if query fails
        """
        try:
            query = f"PRAGMA table_info({table_name})"
            return self.execute_query(query)
        except sqlite3.Error as e:
            logger.error(f"Error getting table info: {e}")
            return None
    
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            bool: True if table exists, False otherwise
        """
        try:
            query = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            result = self.execute_query(query, (table_name,))
            return result is not None and len(result) > 0
        except sqlite3.Error as e:
            logger.error(f"Error checking table existence: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
