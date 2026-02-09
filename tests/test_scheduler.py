# Unit tests for scheduler

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from datetime import datetime, timedelta
from models import Order, MenuItem, DrinkType, Barista
from scheduler import BaristaScheduler

def test_barista_availability():
    """Test barista availability checking"""
    baristas = [Barista(barista_id="B1", name="Barista 1")]
    scheduler = BaristaScheduler(baristas)
    
    current_time = datetime.now()
    
    # Initially available
    available = scheduler.get_available_baristas(current_time)
    assert len(available) == 1, "Should have 1 available barista"
    
    # Assign order
    drink = MenuItem(DrinkType.ESPRESSO, 2, 150, 20)
    order = Order(drinks=[drink])
    baristas[0].assign_order(order, current_time)
    
    # Should not be available until order is done
    available = scheduler.get_available_baristas(current_time)
    assert len(available) == 0, "Should have 0 available baristas"
    
    # After order completion time, should be available
    future_time = current_time + timedelta(minutes=3)
    available = scheduler.get_available_baristas(future_time)
    assert len(available) == 1, "Should have 1 available barista after completion"
    
    print("[PASS] Barista availability test passed")

def test_workload_calculation():
    """Test workload ratio calculation"""
    baristas = [
        Barista(barista_id="B1", name="Barista 1"),
        Barista(barista_id="B2", name="Barista 2"),
        Barista(barista_id="B3", name="Barista 3")
    ]
    
    # Set different workloads
    baristas[0].total_minutes_worked = 60
    baristas[1].total_minutes_worked = 60
    baristas[2].total_minutes_worked = 30  # Underloaded
    
    scheduler = BaristaScheduler(baristas)
    
    # Average is 50 minutes
    ratio_b1 = scheduler.calculate_workload_ratio(baristas[0])
    ratio_b3 = scheduler.calculate_workload_ratio(baristas[2])
    
    assert ratio_b1 > 1.0, "Barista 1 should be above average (1.2x)"
    assert ratio_b3 < 1.0, "Barista 3 should be below average (0.6x)"
    
    print("[PASS] Workload calculation test passed")

def test_order_assignment():
    """Test order assignment to baristas"""
    baristas = [
        Barista(barista_id="B1", name="Barista 1"),
        Barista(barista_id="B2", name="Barista 2")
    ]
    scheduler = BaristaScheduler(baristas)
    
    # Add test orders
    drink = MenuItem(DrinkType.ESPRESSO, 2, 150, 20)
    order1 = Order(drinks=[drink])
    order2 = Order(drinks=[drink])
    
    scheduler.add_order(order1)
    scheduler.add_order(order2)
    
    current_time = datetime.now()
    
    # Assign orders
    assignments = scheduler.assign_orders(current_time)
    
    assert len(assignments) == 2, "Should assign both orders"
    assert baristas[0].current_order is not None, "Barista 1 should have an order"
    assert baristas[1].current_order is not None, "Barista 2 should have an order"
    
    print("[PASS] Order assignment test passed")

def test_emergency_handling():
    """Test emergency order handling"""
    baristas = [
        Barista(barista_id="B1", name="Barista 1"),
        Barista(barista_id="B2", name="Barista 2")
    ]
    
    # Barista 1 is overloaded
    baristas[0].total_minutes_worked = 100
    baristas[1].total_minutes_worked = 20
    
    scheduler = BaristaScheduler(baristas)
    
    drink = MenuItem(DrinkType.ESPRESSO, 2, 150, 20)
    
    # Emergency order (9 min wait)
    emergency_order = Order(
        drinks=[drink],
        arrival_time=datetime.now() - timedelta(minutes=9)
    )
    
    # Even though B1 is overloaded, emergency should go to least busy (B2)
    available = [baristas[1]]
    selected = scheduler.select_barista_for_order(emergency_order, available)
    
    assert selected == baristas[1], "Emergency order should go to least busy barista"
    
    print("[PASS] Emergency handling test passed")

def test_workload_distribution():
    """Test workload distribution calculation"""
    baristas = [
        Barista(barista_id="B1", name="Barista 1"),
        Barista(barista_id="B2", name="Barista 2"),
        Barista(barista_id="B3", name="Barista 3")
    ]
    
    baristas[0].total_minutes_worked = 60
    baristas[1].total_minutes_worked = 60
    baristas[2].total_minutes_worked = 60
    
    scheduler = BaristaScheduler(baristas)
    
    distribution = scheduler.get_workload_distribution()
    
    assert distribution['average'] == 60, "Average should be 60"
    assert distribution['std_dev'] == 0, "Std dev should be 0 for equal distribution"
    assert distribution['balance_percentage'] == 100, "Balance should be 100%"
    
    print("[PASS] Workload distribution test passed")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running Scheduler Tests")
    print("="*60 + "\n")
    
    test_barista_availability()
    test_workload_calculation()
    test_order_assignment()
    test_emergency_handling()
    test_workload_distribution()
    
    print("\n" + "="*60)
    print("All Tests Passed! [SUCCESS]")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_all_tests()
