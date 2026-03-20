"""
DatabaseManager - Beige.AI Retail Intelligence System
=======================================================
Manages persistent storage for recommendation analytics and inventory tracking.

Features:
- SQLite-based purchase history tracking
- Inventory management with reorder alerts
- Conversion rate analytics
- Context-aware popularity analysis
- Thread-safe database operations
- Parameterized SQL queries to prevent injection attacks
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import pandas as pd


class DatabaseManager:
    """
    Thread-safe SQLite database manager for Beige.AI analytics and inventory.
    
    Manages:
    - Purchase history (recommendations → conversions)
    - Inventory levels and reorder tracking
    - Performance analytics by context (mood, weather)
    """
    
    def __init__(self, database_path: str = None):
        """
        Initialize DatabaseManager with database file location.
        
        Args:
            database_path: Path to SQLite database file.
                          Defaults to beige_ai.db in project root.
        """
        if database_path is None:
            # Use root directory
            project_root = Path(__file__).resolve().parents[2]
            database_path = str(project_root / "beige_ai.db")
        
        self.database_path = database_path
        self._local = threading.local()  # Thread-local storage for connections
        
        # Initialize database schema on first use
        self.initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get thread-local database connection.
        Creates new connection if thread doesn't have one.
        
        Returns:
            sqlite3.Connection object
        """
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False,
                isolation_level=None  # Autocommit mode
            )
            self._local.connection.row_factory = sqlite3.Row
        
        return self._local.connection
    
    def _execute_transaction(self, queries: List[Tuple]):
        """
        Execute multiple SQL queries within a transaction.
        Ensures atomicity - all succeed or all rollback.
        
        Args:
            queries: List of (sql_string, parameters_tuple) tuples
        
        Returns:
            List of cursor objects or results
        """
        conn = self._get_connection()
        conn.isolation_level = "DEFERRED"  # Begin transaction
        
        try:
            cursor = conn.cursor()
            results = []
            
            for sql, params in queries:
                cursor.execute(sql, params)
                results.append(cursor)
            
            conn.commit()
            return results
        
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Database transaction failed: {e}")
        
        finally:
            conn.isolation_level = None  # Back to autocommit
    
    def initialize_database(self) -> None:
        """
        Create database schema if it doesn't exist.
        
        Tables:
        - purchase_history: Tracks recommendation → purchase conversions
        - inventory: Current stock levels and reorder thresholds
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create purchase_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchase_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                recommended_cake TEXT NOT NULL,
                selected_cake TEXT,
                is_conversion BOOLEAN DEFAULT 0,
                mood TEXT,
                weather TEXT
            )
        """)
        
        # Create inventory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                cake_name TEXT PRIMARY KEY,
                stock_quantity INTEGER DEFAULT 0,
                reorder_level INTEGER DEFAULT 5
            )
        """)
        
        # Create indices for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_purchase_timestamp
            ON purchase_history(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_purchase_mood
            ON purchase_history(mood)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_purchase_weather
            ON purchase_history(weather)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_inventory_reorder
            ON inventory(stock_quantity, reorder_level)
        """)
        
        conn.commit()
    
    def initialize_inventory(self, cake_list: List[str], initial_stock: int = 20, reorder_level: int = 5) -> None:
        """
        Initialize inventory for all cakes in the menu.
        Skips cakes that already exist.
        
        Args:
            cake_list: List of cake names from menu
            initial_stock: Initial quantity for new items
            reorder_level: Threshold for low stock alerts
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        for cake in cake_list:
            # Use INSERT OR IGNORE to skip existing entries
            cursor.execute("""
                INSERT OR IGNORE INTO inventory 
                (cake_name, stock_quantity, reorder_level)
                VALUES (?, ?, ?)
            """, (cake, initial_stock, reorder_level))
        
        conn.commit()
    
    def record_purchase(
        self,
        recommended_cake: str,
        selected_cake: Optional[str] = None,
        mood: Optional[str] = None,
        weather: Optional[str] = None
    ) -> int:
        """
        Record a recommendation and its conversion outcome.
        
        Args:
            recommended_cake: Name of AI-recommended cake
            selected_cake: Customer's actual choice (None if no purchase)
            mood: Customer's mood at time of recommendation
            weather: Weather conditions at time of recommendation
        
        Returns:
            ID of inserted record
        """
        is_conversion = (selected_cake is not None and selected_cake != "No Purchase")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO purchase_history
            (recommended_cake, selected_cake, is_conversion, mood, weather)
            VALUES (?, ?, ?, ?, ?)
        """, (recommended_cake, selected_cake, is_conversion, mood, weather))
        
        conn.commit()
        return cursor.lastrowid
    
    def update_inventory(self, cake_name: str, quantity_delta: int = -1) -> bool:
        """
        Update inventory after a purchase (decrement) or restock (increment).
        Prevents negative inventory.
        
        Args:
            cake_name: Name of cake to update
            quantity_delta: Change in quantity (-1 for sale, +10 for restock)
        
        Returns:
            True if successful, False if would go negative
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # First, get current stock
            cursor.execute(
                "SELECT stock_quantity FROM inventory WHERE cake_name = ?",
                (cake_name,)
            )
            row = cursor.fetchone()
            
            if row is None:
                # Initialize if not exists
                cursor.execute("""
                    INSERT INTO inventory (cake_name, stock_quantity, reorder_level)
                    VALUES (?, ?, ?)
                """, (cake_name, max(0, quantity_delta), 5))
                conn.commit()
                return quantity_delta >= 0
            
            current_stock = row[0]
            new_stock = current_stock + quantity_delta
            
            # Prevent negative inventory
            if new_stock < 0:
                return False
            
            # Update inventory
            cursor.execute(
                "UPDATE inventory SET stock_quantity = ? WHERE cake_name = ?",
                (new_stock, cake_name)
            )
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f"Inventory update failed for {cake_name}: {e}")
            return False
    
    def get_conversion_rate(self, days: int = 7) -> float:
        """
        Calculate conversion rate (purchases / recommendations) for recent period.
        
        Args:
            days: Number of days to analyze (default: 7)
        
        Returns:
            Conversion rate as percentage (0-100)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_recommendations,
                SUM(CASE WHEN is_conversion = 1 THEN 1 ELSE 0 END) as conversions
            FROM purchase_history
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
        """, (days,))
        
        row = cursor.fetchone()
        
        if row and row[0] > 0:
            total = row[0]
            conversions = row[1] or 0
            return (conversions / total) * 100
        
        return 0.0
    
    def get_low_stock_items(self) -> List[Dict]:
        """
        Get all inventory items below reorder level.
        
        Returns:
            List of dicts: [{'cake_name': str, 'stock': int, 'reorder_level': int}, ...]
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cake_name, stock_quantity, reorder_level
            FROM inventory
            WHERE stock_quantity <= reorder_level
            ORDER BY stock_quantity ASC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'cake_name': row[0],
                'stock': row[1],
                'reorder_level': row[2]
            })
        
        return results
    
    def get_popularity_by_context(self, limit: int = 10) -> pd.DataFrame:
        """
        Analyze most purchased cakes grouped by mood and weather context.
        
        Args:
            limit: Maximum number of records per context combination
        
        Returns:
            DataFrame with columns: mood, weather, selected_cake, purchase_count
        """
        conn = self._get_connection()
        
        query = """
            SELECT 
                COALESCE(mood, 'Unknown') as mood,
                COALESCE(weather, 'Unknown') as weather,
                selected_cake,
                COUNT(*) as purchase_count
            FROM purchase_history
            WHERE is_conversion = 1 AND selected_cake IS NOT NULL
            GROUP BY mood, weather, selected_cake
            ORDER BY purchase_count DESC
            LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=(limit,))
        return df
    
    def get_recommendation_accuracy(self, days: int = 7) -> float:
        """
        Calculate how often recommended cake matches selected cake.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Accuracy rate as percentage (0-100)
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN recommended_cake = selected_cake THEN 1 ELSE 0 END) as accurate
            FROM purchase_history
            WHERE is_conversion = 1 
            AND timestamp >= datetime('now', '-' || ? || ' days')
        """, (days,))
        
        row = cursor.fetchone()
        
        if row and row[0] > 0:
            total = row[0]
            accurate = row[1] or 0
            return (accurate / total) * 100
        
        return 0.0
    
    def get_total_inventory_value(self) -> Dict[str, float]:
        """
        Get total quantity and estimated inventory metrics.
        
        Returns:
            Dict with total_items, cakes_in_stock, cakes_low_stock
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(stock_quantity) as total_items,
                COUNT(CASE WHEN stock_quantity > 0 THEN 1 END) as cakes_in_stock,
                COUNT(CASE WHEN stock_quantity <= reorder_level THEN 1 END) as cakes_low_stock
            FROM inventory
        """)
        
        row = cursor.fetchone()
        
        return {
            'total_items': row[0] or 0,
            'cakes_in_stock': row[1] or 0,
            'cakes_low_stock': row[2] or 0
        }
    
    def get_purchase_history_dataframe(self, days: int = 30) -> pd.DataFrame:
        """
        Get full purchase history as pandas DataFrame for analysis.
        
        Args:
            days: Number of days of history to retrieve
        
        Returns:
            DataFrame with all purchase records
        """
        conn = self._get_connection()
        
        query = """
            SELECT 
                id, timestamp, recommended_cake, selected_cake, 
                is_conversion, mood, weather
            FROM purchase_history
            WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(days,))
        
        # Convert timestamp to datetime
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['is_conversion'] = df['is_conversion'].astype(bool)
        
        return df
    
    def close(self) -> None:
        """Close the database connection."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None


# ============================================================================
# Singleton Pattern for Global Database Access
# ============================================================================

_db_instance: Optional[DatabaseManager] = None
_db_lock = threading.Lock()


def get_database_manager(database_path: str = None) -> DatabaseManager:
    """
    Get or create the global DatabaseManager instance.
    
    Args:
        database_path: Path to database file (only used on first call)
    
    Returns:
        Singleton DatabaseManager instance
    """
    global _db_instance
    
    if _db_instance is None:
        with _db_lock:
            if _db_instance is None:
                _db_instance = DatabaseManager(database_path)
    
    return _db_instance
