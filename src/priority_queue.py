# Priority Queue implementation with dynamic scoring

from typing import List
from datetime import datetime
import heapq
from models import Order, CustomerType
from config import PRIORITY_WEIGHTS, MAX_SKIP_COUNT, EMERGENCY_THRESHOLD

class PriorityCalculator:
    """Calculates priority scores for orders based on multiple factors"""
    
    def __init__(self):
        self.weights = PRIORITY_WEIGHTS
    
    def calculate_wait_time_score(self, order: Order) -> float:
        """
        Calculate wait time component (0-100)
        Linear increase: 0 at 0 min, 100 at 10 min
        """
        wait_minutes = order.wait_time_minutes
        return min(100, (wait_minutes / 10) * 100)
    
    def calculate_complexity_score(self, order: Order) -> float:
        """
        Calculate complexity component (0-100)
        Shorter orders get higher scores for throughput
        Inverse relationship: 6min = 0, 1min = 100
        """
        prep_time = order.total_prep_time
        # Max prep time is ~6 min, min is 1 min
        max_prep = 6
        min_prep = 1
        normalized = (max_prep - prep_time) / (max_prep - min_prep)
        return max(0, min(100, normalized * 100))
    
    def calculate_loyalty_score(self, order: Order) -> float:
        """
        Calculate loyalty component (0-100)
        Gold members get boost
        """
        loyalty_scores = {
            CustomerType.NEW: 0,
            CustomerType.REGULAR: 50,
            CustomerType.GOLD: 100
        }
        return loyalty_scores.get(order.customer_type, 50)
    
    def calculate_urgency_score(self, order: Order) -> float:
        """
        Calculate urgency component (0-100)
        Exponential increase as approaching timeout
        """
        wait_minutes = order.wait_time_minutes
        
        # Emergency boost if > 8 minutes
        if wait_minutes >= EMERGENCY_THRESHOLD:
            # Exponential scaling from 8 to 10 minutes
            excess = wait_minutes - EMERGENCY_THRESHOLD
            return min(100, 50 + (excess / 2) * 50)
        else:
            # Low urgency before 8 minutes
            return (wait_minutes / EMERGENCY_THRESHOLD) * 50
    
    def calculate_fairness_penalty(self, order: Order) -> float:
        """
        Calculate penalty for orders that have been skipped too many times
        """
        if order.skip_count > MAX_SKIP_COUNT:
            # Add 50 points for excessive skipping
            return 50
        return 0
    
    def calculate_priority(self, order: Order) -> float:
        """
        Calculate overall priority score (0-100+)
        Higher score = higher priority
        """
        wait_score = self.calculate_wait_time_score(order)
        complexity_score = self.calculate_complexity_score(order)
        loyalty_score = self.calculate_loyalty_score(order)
        urgency_score = self.calculate_urgency_score(order)
        fairness_bonus = self.calculate_fairness_penalty(order)
        
        # Weighted sum
        priority = (
            wait_score * self.weights['wait_time'] +
            complexity_score * self.weights['complexity'] +
            loyalty_score * self.weights['loyalty'] +
            urgency_score * self.weights['urgency'] +
            fairness_bonus  # Additive bonus
        )
        
        return priority

class OrderQueue:
    """Priority queue for managing waiting orders"""
    
    def __init__(self):
        self.calculator = PriorityCalculator()
        self.waiting_orders: List[Order] = []
        self.heap: List[tuple] = []  # (negative_priority, order_id, order)
    
    def add_order(self, order: Order):
        """Add a new order to the queue"""
        self.waiting_orders.append(order)
        self._update_priorities()
    
    def _update_priorities(self):
        """Recalculate all priorities and rebuild heap"""
        self.heap = []
        for order in self.waiting_orders:
            priority = self.calculator.calculate_priority(order)
            order.priority_score = priority
            # Use negative priority for max heap behavior
            heapq.heappush(self.heap, (-priority, order.order_id, order))
    
    def get_highest_priority_order(self) -> Order:
        """Get and remove the highest priority order"""
        if not self.heap:
            return None
        
        # Rebuild heap to ensure current priorities
        self._update_priorities()
        
        _, _, order = heapq.heappop(self.heap)
        self.waiting_orders.remove(order)
        return order
    
    def peek_top_orders(self, n: int = 5) -> List[Order]:
        """View top N orders without removing them"""
        self._update_priorities()
        sorted_orders = sorted(self.heap, key=lambda x: x[0])
        return [order for _, _, order in sorted_orders[:n]]
    
    def update_skip_counts(self, served_order: Order):
        """
        Update skip counts for orders that arrived before the served order
        but are still waiting
        """
        for order in self.waiting_orders:
            if order.arrival_time < served_order.arrival_time:
                order.skip_count += 1
    
    def get_emergency_orders(self) -> List[Order]:
        """Get all orders approaching timeout"""
        return [order for order in self.waiting_orders if order.is_timeout_risk]
    
    def size(self) -> int:
        """Get number of waiting orders"""
        return len(self.waiting_orders)
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.waiting_orders) == 0
    
    def __str__(self):
        if self.is_empty():
            return "Queue: Empty"
        
        top_5 = self.peek_top_orders(5)
        orders_str = "\n".join([
            f"  {i+1}. {order} (Priority: {order.priority_score:.1f})"
            for i, order in enumerate(top_5)
        ])
        return f"Queue ({self.size()} orders):\n{orders_str}"
