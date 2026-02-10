"""
Simple test script to verify database and core functionality
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from database import Database
from config import MENU_ITEMS, NUM_BARISTAS, CUSTOMER_ARRIVAL_RATE

def test_database():
    """Test database initialization and basic operations."""
    print("Testing Database Layer...")
    
    # Initialize database
    db = Database("test_barista_queue.db")
    print("[OK] Database initialized successfully")
    
    # Create a test simulation run
    run_id = db.create_simulation_run(
        run_type='priority_queue',
        num_baristas=NUM_BARISTAS,
        customer_arrival_rate=CUSTOMER_ARRIVAL_RATE
    )
    print(f"[OK] Created simulation run with ID: {run_id}")
    
    # Insert a test order
    order_data = {
        'order_number': 1,
        'customer_type': 'REGULAR',
        'drink_type': 'COLD_BREW',
        'drink_name': 'Cold Brew',
        'prep_time': 1.0,
        'price': 120,
        'arrival_time': 0.0,
        'priority_score': 50.0,
        'status': 'pending'
    }
    
    order_id = db.insert_order(run_id, order_data)
    print(f"[OK] Created test order with ID: {order_id}")
    
    # Insert a test barista
    barista_data = {
        'barista_id': 1,
        'name': 'Barista 1',
        'total_orders': 0,
        'total_minutes': 0.0,
        'is_busy': 0,
        'available_at': 0.0
    }
    
    barista_id = db.insert_barista(run_id, barista_data)
    print(f"[OK] Created test barista with ID: {barista_id}")
    
    # Retrieve data
    orders = db.get_orders_by_simulation(run_id)
    print(f"[OK] Retrieved {len(orders)} order(s)")
    
    baristas = db.get_baristas_by_simulation(run_id)
    print(f"[OK] Retrieved {len(baristas)} barista(s)")
    
    # Update simulation with metrics
    metrics = {
        'total_customers': 1,
        'avg_wait_time': 2.5,
        'max_wait_time': 5.0,
        'timeout_rate': 0.0,
        'workload_balance': 1.0
    }
    
    db.update_simulation_run(run_id, metrics)
    print("[OK] Updated simulation run with metrics")
    
    # Get simulation run
    sim_run = db.get_simulation_run(run_id)
    print(f"[OK] Retrieved simulation run: {sim_run['run_type']}")
    
    # Clean up test database
    import os
    if os.path.exists("test_barista_queue.db"):
        os.remove("test_barista_queue.db")
        print("[OK] Cleaned up test database")
    
    print("\nAll database tests passed!")

def test_config():
    """Test configuration loading."""
    print("\nTesting Configuration...")
    
    print(f"[OK] Number of baristas: {NUM_BARISTAS}")
    print(f"[OK] Customer arrival rate: {CUSTOMER_ARRIVAL_RATE}")
    print(f"[OK] Menu items loaded: {len(MENU_ITEMS)}")
    
    # Display menu
    print("\nMenu Items:")
    for key, item in MENU_ITEMS.items():
        print(f"  - {item.name}: Rs.{item.price_inr} ({item.prep_time_minutes} min)")
    
    print("\nConfiguration tests passed!")

def test_imports():
    """Test that all required modules can be imported."""
    print("\nTesting Module Imports...")
    
    try:
        import streamlit
        print("[OK] Streamlit imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import Streamlit: {e}")
        return False
    
    try:
        import plotly
        print("[OK] Plotly imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import Plotly: {e}")
        return False
    
    try:
        import pandas
        print("[OK] Pandas imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import Pandas: {e}")
        return False
    
    try:
        import numpy
        print("[OK] Numpy imported successfully")
    except ImportError as e:
        print(f"[FAIL] Failed to import Numpy: {e}")
        return False
    
    print("\nAll imports successful!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Barista Queue System - Verification Tests")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\nImport tests failed. Please install dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Test configuration
    test_config()
    
    # Test database
    test_database()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
    print("\nNext Steps:")
    print("   1. Run the Streamlit dashboard:")
    print("      streamlit run app.py")
    print("   2. Open http://localhost:8501 in your browser")
    print("   3. Explore the features and run simulations!")
    print("\nEnjoy your coffee shop queue system!")
