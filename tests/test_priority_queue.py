# Unit tests for priority queue

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from datetime import datetime, timedelta
from models import Order, MenuItem, DrinkType, CustomerType
from priority_queue import PriorityCalculator, OrderQueue

def test_priority_calculator_wait_time():
    """Test wait time score calculation"""
    calc = PriorityCalculator()
    
    # Create order with specific arrival time
    drink = MenuItem(DrinkType.ESPRESSO, 2, 150, 20)
    order = Order(drinks=[drink], arrival_time=datetime.now() - timedelta(minutes=5))
    
    score = calc.calculate_wait_time_score(order)
    
    # Wait time of 5 min should give score of ~50
    assert 40 <= score <= 60, f"Expected score around 50, got {score}"
    print("[PASS] Wait time score test passed")

def test_priority_calculator_complexity():
    """Test complexity score calculation"""
    calc = PriorityCalculator()
    
    # Quick drink (1 min)
    quick_drink = MenuItem(DrinkType.COLD_BREW, 1, 120, 25)
    quick_order = Order(drinks=[quick_drink])
    
    # Slow drink (6 min)
    slow_drink = MenuItem(DrinkType.SPECIALTY, 6, 250, 8)
    slow_order = Order(drinks=[slow_drink])
    
    quick_score = calc.calculate_complexity_score(quick_order)
    slow_score = calc.calculate_complexity_score(slow_order)
    
    # Quick orders should score higher
    assert quick_score > slow_score, "Quick orders should have higher complexity score"
    print("[PASS] Complexity score test passed")

def test_priority_calculator_urgency():
    """Test urgency score with emergency threshold"""
    calc = PriorityCalculator()
    
    drink = MenuItem(DrinkType.ESPRESSO, 2, 150, 20)
    
    # Normal order (3 min wait)
    normal_order = Order(drinks=[drink], arrival_time=datetime.now() - timedelta(minutes=3))
    
    # Emergency order (9 min wait)
    emergency_order = Order(drinks=[drink], arrival_time=datetime.now() - timedelta(minutes=9))
    
    normal_urgency = calc.calculate_urgency_score(normal_order)
    emergency_urgency = calc.calculate_urgency_score(emergency_order)
    
    # Emergency should score much higher
    assert emergency_urgency > normal_urgency * 2, "Emergency orders should have much higher urgency"
    print("[PASS] Urgency score test passed")

def test_order_queue_priority_ordering():
    """Test that queue returns orders in priority order"""
    queue = OrderQueue()
    
    # Add orders with different wait times
    drink = MenuItem(DrinkType.ESPRESSO, 2, 150, 20)
    
    order1 = Order(drinks=[drink], arrival_time=datetime.now() - timedelta(minutes=2))
    order2 = Order(drinks=[drink], arrival_time=datetime.now() - timedelta(minutes=8))
    order3 = Order(drinks=[drink], arrival_time=datetime.now() - timedelta(minutes=5))
    
    queue.add_order(order1)
    queue.add_order(order2)
    queue.add_order(order3)
    
    # Get highest priority - should be order2 (longest wait)
    top_order = queue.get_highest_priority_order()
    
    assert top_order == order2, "Order with longest wait should have highest priority"
    assert queue.size() == 2, "Queue should have 2 orders remaining"
    print("[PASS] Queue priority ordering test passed")

def test_skip_count_update():
    """Test skip count tracking"""
    queue = OrderQueue()
    
    drink = MenuItem(DrinkType.ESPRESSO, 2, 150, 20)
    
    # Order 1 arrives first
    order1 = Order(drinks=[drink], arrival_time=datetime.now() - timedelta(minutes=5))
    # Order 2 arrives later
    order2 = Order(drinks=[drink], arrival_time=datetime.now() - timedelta(minutes=2))
    
    queue.add_order(order1)
    queue.add_order(order2)
    
    # If order2 is served first, order1's skip count should increase
    queue.update_skip_counts(order2)
    
    assert order1.skip_count == 1, "Skip count should be incremented for earlier orders"
    assert order2.skip_count == 0, "Served order skip count should remain 0"
    print("[PASS] Skip count update test passed")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running Priority Queue Tests")
    print("="*60 + "\n")
    
    test_priority_calculator_wait_time()
    test_priority_calculator_complexity()
    test_priority_calculator_urgency()
    test_order_queue_priority_ordering()
    test_skip_count_update()
    
    print("\n" + "="*60)
    print("All Tests Passed! [SUCCESS]")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_all_tests()
