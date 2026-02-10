"""
Database layer for the Barista Queue System.
Handles SQLite database operations for orders, baristas, metrics, and simulation runs.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from contextlib import contextmanager


class Database:
    """SQLite database manager for the barista queue system."""
    
    def __init__(self, db_path: str = "barista_queue.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Simulation runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS simulation_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_type TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    num_baristas INTEGER,
                    customer_arrival_rate REAL,
                    total_customers INTEGER,
                    avg_wait_time REAL,
                    max_wait_time REAL,
                    timeout_rate REAL,
                    workload_balance REAL,
                    status TEXT DEFAULT 'running'
                )
            """)
            
            # Orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_run_id INTEGER,
                    order_number INTEGER,
                    customer_type TEXT,
                    drink_type TEXT,
                    drink_name TEXT,
                    prep_time REAL,
                    price REAL,
                    arrival_time REAL,
                    start_time REAL,
                    completion_time REAL,
                    wait_time REAL,
                    assigned_barista_id INTEGER,
                    priority_score REAL,
                    skip_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (simulation_run_id) REFERENCES simulation_runs(id)
                )
            """)
            
            # Baristas table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS baristas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_run_id INTEGER,
                    barista_id INTEGER,
                    name TEXT,
                    total_orders INTEGER DEFAULT 0,
                    total_minutes REAL DEFAULT 0,
                    is_busy INTEGER DEFAULT 0,
                    current_order_id INTEGER,
                    available_at REAL DEFAULT 0,
                    FOREIGN KEY (simulation_run_id) REFERENCES simulation_runs(id)
                )
            """)
            
            # Metrics snapshots table (for time-series data)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_run_id INTEGER,
                    timestamp REAL,
                    queue_length INTEGER,
                    avg_wait_time REAL,
                    orders_completed INTEGER,
                    orders_pending INTEGER,
                    barista_utilization TEXT,
                    FOREIGN KEY (simulation_run_id) REFERENCES simulation_runs(id)
                )
            """)
            
            # Events log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_run_id INTEGER,
                    timestamp REAL,
                    event_type TEXT,
                    order_id INTEGER,
                    barista_id INTEGER,
                    details TEXT,
                    FOREIGN KEY (simulation_run_id) REFERENCES simulation_runs(id)
                )
            """)
            
            conn.commit()
    
    # Simulation Run Operations
    def create_simulation_run(self, run_type: str, num_baristas: int, 
                            customer_arrival_rate: float) -> int:
        """Create a new simulation run record.
        
        Args:
            run_type: Type of simulation (e.g., 'priority_queue', 'fifo')
            num_baristas: Number of baristas
            customer_arrival_rate: Lambda for Poisson arrival
            
        Returns:
            Simulation run ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO simulation_runs 
                (run_type, num_baristas, customer_arrival_rate, status)
                VALUES (?, ?, ?, 'running')
            """, (run_type, num_baristas, customer_arrival_rate))
            return cursor.lastrowid
    
    def update_simulation_run(self, run_id: int, metrics: Dict[str, Any]):
        """Update simulation run with final metrics.
        
        Args:
            run_id: Simulation run ID
            metrics: Dictionary of metrics to update
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE simulation_runs
                SET end_time = CURRENT_TIMESTAMP,
                    total_customers = ?,
                    avg_wait_time = ?,
                    max_wait_time = ?,
                    timeout_rate = ?,
                    workload_balance = ?,
                    status = 'completed'
                WHERE id = ?
            """, (
                metrics.get('total_customers', 0),
                metrics.get('avg_wait_time', 0),
                metrics.get('max_wait_time', 0),
                metrics.get('timeout_rate', 0),
                metrics.get('workload_balance', 0),
                run_id
            ))
    
    def get_simulation_run(self, run_id: int) -> Optional[Dict]:
        """Get simulation run by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM simulation_runs WHERE id = ?", (run_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_recent_simulation_runs(self, limit: int = 10) -> List[Dict]:
        """Get recent simulation runs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM simulation_runs 
                ORDER BY start_time DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Order Operations
    def insert_order(self, simulation_run_id: int, order_data: Dict[str, Any]) -> int:
        """Insert a new order.
        
        Args:
            simulation_run_id: Associated simulation run ID
            order_data: Order details dictionary
            
        Returns:
            Order ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (
                    simulation_run_id, order_number, customer_type, drink_type,
                    drink_name, prep_time, price, arrival_time, priority_score, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                simulation_run_id,
                order_data.get('order_number'),
                order_data.get('customer_type'),
                order_data.get('drink_type'),
                order_data.get('drink_name'),
                order_data.get('prep_time'),
                order_data.get('price'),
                order_data.get('arrival_time'),
                order_data.get('priority_score', 0),
                order_data.get('status', 'pending')
            ))
            return cursor.lastrowid
    
    def update_order(self, order_id: int, updates: Dict[str, Any]):
        """Update order details."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            for key, value in updates.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            values.append(order_id)
            query = f"UPDATE orders SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
    
    def get_orders_by_simulation(self, simulation_run_id: int) -> List[Dict]:
        """Get all orders for a simulation run."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM orders 
                WHERE simulation_run_id = ?
                ORDER BY arrival_time
            """, (simulation_run_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_pending_orders(self, simulation_run_id: int) -> List[Dict]:
        """Get pending orders for a simulation run."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM orders 
                WHERE simulation_run_id = ? AND status = 'pending'
                ORDER BY priority_score DESC
            """, (simulation_run_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Barista Operations
    def insert_barista(self, simulation_run_id: int, barista_data: Dict[str, Any]) -> int:
        """Insert a barista record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO baristas (
                    simulation_run_id, barista_id, name, total_orders, 
                    total_minutes, is_busy, available_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                simulation_run_id,
                barista_data.get('barista_id'),
                barista_data.get('name'),
                barista_data.get('total_orders', 0),
                barista_data.get('total_minutes', 0),
                barista_data.get('is_busy', 0),
                barista_data.get('available_at', 0)
            ))
            return cursor.lastrowid
    
    def update_barista(self, barista_id: int, updates: Dict[str, Any]):
        """Update barista status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            for key, value in updates.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            values.append(barista_id)
            query = f"UPDATE baristas SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
    
    def get_baristas_by_simulation(self, simulation_run_id: int) -> List[Dict]:
        """Get all baristas for a simulation run."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM baristas 
                WHERE simulation_run_id = ?
                ORDER BY barista_id
            """, (simulation_run_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # Metrics Operations
    def insert_metrics_snapshot(self, simulation_run_id: int, 
                               timestamp: float, metrics: Dict[str, Any]):
        """Insert a metrics snapshot for time-series tracking."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO metrics_snapshots (
                    simulation_run_id, timestamp, queue_length, avg_wait_time,
                    orders_completed, orders_pending, barista_utilization
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                simulation_run_id,
                timestamp,
                metrics.get('queue_length', 0),
                metrics.get('avg_wait_time', 0),
                metrics.get('orders_completed', 0),
                metrics.get('orders_pending', 0),
                json.dumps(metrics.get('barista_utilization', {}))
            ))
    
    def get_metrics_snapshots(self, simulation_run_id: int) -> List[Dict]:
        """Get all metrics snapshots for a simulation run."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM metrics_snapshots 
                WHERE simulation_run_id = ?
                ORDER BY timestamp
            """, (simulation_run_id,))
            rows = cursor.fetchall()
            
            # Parse JSON fields
            result = []
            for row in rows:
                data = dict(row)
                data['barista_utilization'] = json.loads(data['barista_utilization'])
                result.append(data)
            return result
    
    # Event Logging
    def log_event(self, simulation_run_id: int, timestamp: float, 
                  event_type: str, order_id: Optional[int] = None,
                  barista_id: Optional[int] = None, details: str = ""):
        """Log a simulation event."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (
                    simulation_run_id, timestamp, event_type, 
                    order_id, barista_id, details
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (simulation_run_id, timestamp, event_type, 
                  order_id, barista_id, details))
    
    def get_events(self, simulation_run_id: int, limit: int = 100) -> List[Dict]:
        """Get recent events for a simulation run."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM events 
                WHERE simulation_run_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (simulation_run_id, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    # Analytics Queries
    def get_performance_comparison(self) -> Dict[str, Any]:
        """Get performance comparison across simulation types."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    run_type,
                    AVG(avg_wait_time) as avg_wait,
                    AVG(max_wait_time) as avg_max_wait,
                    AVG(timeout_rate) as avg_timeout_rate,
                    AVG(workload_balance) as avg_workload_balance,
                    COUNT(*) as num_runs
                FROM simulation_runs
                WHERE status = 'completed'
                GROUP BY run_type
            """)
            
            results = {}
            for row in cursor.fetchall():
                results[row['run_type']] = dict(row)
            return results
    
    def clear_database(self):
        """Clear all data from database (for testing)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events")
            cursor.execute("DELETE FROM metrics_snapshots")
            cursor.execute("DELETE FROM baristas")
            cursor.execute("DELETE FROM orders")
            cursor.execute("DELETE FROM simulation_runs")
            conn.commit()
