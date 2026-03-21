"""
RetailDatabaseManager - Beige.AI Checkout & POS System
========================================================
Manages retail operations: basket, checkout, sales tracking, inventory.

Features:
- Sales transaction logging
- Real-time inventory management
- Recommendation match tracking
- Mood-based sales analysis
- Thread-safe operations
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import pandas as pd


class RetailDatabaseManager:
    """
    Thread-safe SQLite manager for Beige.AI retail operations.
    Tracks sales, manages inventory, monitors conversion metrics.
    """
    
    def __init__(self, database_path: str = None):
        """
        Initialize RetailDatabaseManager with database file location.
        
        Args:
            database_path: Path to SQLite database file.
                          Defaults to beige_retail.db in data/ directory.
        """
        if database_path is None:
            project_root = Path(__file__).resolve().parents[2]
            data_dir = project_root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            database_path = str(data_dir / "beige_retail.db")
        
        self.database_path = database_path
        self._local = threading.local()
        self.initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False,
                isolation_level=None
            )
            self._local.connection.row_factory = sqlite3.Row
        
        return self._local.connection
    
    def initialize_database(self) -> None:
        """Create database schema if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create sales table - tracks every purchase
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                recommended_cake TEXT NOT NULL,
                bought_cake TEXT NOT NULL,
                is_match INTEGER DEFAULT 0,
                mood TEXT,
                weather TEXT,
                price REAL NOT NULL
            )
        """)
        
        # Create inventory table - tracks stock levels
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                cake_name TEXT PRIMARY KEY,
                current_stock INTEGER DEFAULT 0,
                unit_price REAL DEFAULT 0.0
            )
        """)
        
        # Create indices for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_timestamp
            ON sales(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_mood
            ON sales(mood)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_match
            ON sales(is_match)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_inventory_stock
            ON inventory(current_stock)
        """)
        
        conn.commit()
    
    def initialize_inventory_from_menu(self, cake_menu: Dict[str, float]) -> None:
        """
        Initialize or update inventory for all cakes.
        
        Args:
            cake_menu: Dict with cake_name -> unit_price mapping
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for cake_name, unit_price in cake_menu.items():
            cursor.execute("""
                INSERT OR IGNORE INTO inventory 
                (cake_name, current_stock, unit_price)
                VALUES (?, ?, ?)
            """, (cake_name, 50, unit_price))
        
        conn.commit()
    
    def process_sale(
        self,
        recommended_cake: str,
        bought_cake: str,
        mood: Optional[str] = None,
        weather: Optional[str] = None,
        price: float = 0.0
    ) -> Tuple[bool, int]:
        """
        Record a sale and update inventory.
        
        Args:
            recommended_cake: AI's recommendation
            bought_cake: What customer actually purchased
            mood: Customer's mood
            weather: Environmental condition
            price: Sale price
        
        Returns:
            (success: bool, sale_id: int)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if cake is in stock
            cursor.execute(
                "SELECT current_stock FROM inventory WHERE cake_name = ?",
                (bought_cake,)
            )
            row = cursor.fetchone()
            
            if row is None or row[0] <= 0:
                return False, -1
            
            # Calculate match
            is_match = 1 if bought_cake == recommended_cake else 0
            
            # Insert sale record
            cursor.execute("""
                INSERT INTO sales
                (recommended_cake, bought_cake, is_match, mood, weather, price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (recommended_cake, bought_cake, is_match, mood, weather, price))
            
            sale_id = cursor.lastrowid
            
            # Update inventory
            cursor.execute("""
                UPDATE inventory 
                SET current_stock = current_stock - 1 
                WHERE cake_name = ?
            """, (bought_cake,))
            
            conn.commit()
            return True, sale_id
        
        except Exception as e:
            conn.rollback()
            print(f"Sale processing error: {e}")
            return False, -1
    
    def get_stock_level(self, cake_name: str) -> int:
        """Get current stock for a cake."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT current_stock FROM inventory WHERE cake_name = ?",
            (cake_name,)
        )
        
        row = cursor.fetchone()
        return row[0] if row else 0
    
    def update_stock(self, cake_name: str, delta: int) -> bool:
        """Update inventory for a cake."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT current_stock FROM inventory WHERE cake_name = ?",
                (cake_name,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return False
            
            new_stock = row[0] + delta
            
            if new_stock < 0:
                return False
            
            cursor.execute(
                "UPDATE inventory SET current_stock = ? WHERE cake_name = ?",
                (new_stock, cake_name)
            )
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f"Stock update error: {e}")
            return False
    
    def get_conversion_rate(self, days: int = 7) -> float:
        """
        Get conversion rate: % of sales matching recommendation.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Conversion rate as percentage (0-100)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sales,
                SUM(CASE WHEN is_match = 1 THEN 1 ELSE 0 END) as matches
            FROM sales
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """, (days,))
        
        row = cursor.fetchone()
        
        if row and row[0] > 0:
            total = row[0]
            matches = row[1] or 0
            return (matches / total) * 100
        
        return 0.0
    
    def get_inventory_status(self) -> pd.DataFrame:
        """
        Get current inventory status for all cakes.
        
        Returns:
            DataFrame with cake_name, current_stock, unit_price
        """
        conn = self._get_connection()
        
        query = """
            SELECT cake_name, current_stock, unit_price
            FROM inventory
            ORDER BY cake_name
        """
        
        df = pd.read_sql_query(query, conn)
        return df
    
    def get_low_stock_items(self, threshold: int = 10) -> pd.DataFrame:
        """Get items below stock threshold."""
        conn = self._get_connection()
        
        query = """
            SELECT cake_name, current_stock, unit_price
            FROM inventory
            WHERE current_stock < ?
            ORDER BY current_stock ASC
        """
        
        df = pd.read_sql_query(query, conn, params=(threshold,))
        return df
    
    def get_sales_by_mood(self, days: int = 30) -> pd.DataFrame:
        """
        Get sales data grouped by mood and cake.
        
        Returns:
            DataFrame with mood, bought_cake, count
        """
        conn = self._get_connection()
        
        query = """
            SELECT 
                COALESCE(mood, 'Unknown') as mood,
                bought_cake,
                COUNT(*) as count,
                SUM(price) as revenue
            FROM sales
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY mood, bought_cake
            ORDER BY count DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(days,))
        return df
    
    def get_total_revenue(self, days: int = 30) -> float:
        """Get total revenue for period."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT SUM(price) as revenue
            FROM sales
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """, (days,))
        
        row = cursor.fetchone()
        return row[0] if row and row[0] else 0.0
    
    def get_daily_sales(self, days: int = 30) -> pd.DataFrame:
        """Get daily sales summary."""
        conn = self._get_connection()
        
        query = """
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_sales,
                SUM(CASE WHEN is_match = 1 THEN 1 ELSE 0 END) as matched,
                SUM(price) as revenue
            FROM sales
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(days,))
        return df
    
    def get_top_selling_cakes(self, limit: int = 8, days: int = 30) -> pd.DataFrame:
        """Get top selling cakes."""
        conn = self._get_connection()
        
        query = """
            SELECT 
                bought_cake as cake,
                COUNT(*) as units_sold,
                SUM(price) as revenue
            FROM sales
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY bought_cake
            ORDER BY units_sold DESC
            LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=(days, limit))
        return df
    
    def get_sales_history(self, days: int = 30, limit: int = 100) -> pd.DataFrame:
        """Get recent sales history."""
        conn = self._get_connection()
        
        query = """
            SELECT 
                id, timestamp, recommended_cake, bought_cake, 
                is_match, mood, weather, price
            FROM sales
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
            LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=(days, limit))
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df


# ============================================================================
# Singleton Pattern for Global Database Access
# ============================================================================

_retail_db_instance: Optional[RetailDatabaseManager] = None
_retail_db_lock = threading.Lock()


def get_retail_database(database_path: str = None) -> RetailDatabaseManager:
    """Get or create the global RetailDatabaseManager instance."""
    global _retail_db_instance
    
    if _retail_db_instance is None:
        with _retail_db_lock:
            if _retail_db_instance is None:
                _retail_db_instance = RetailDatabaseManager(database_path)
    
    return _retail_db_instance
