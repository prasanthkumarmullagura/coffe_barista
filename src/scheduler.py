# Barista scheduling and assignment logic

from typing import List, Optional
from datetime import datetime
from models import Barista, Order
from priority_queue import OrderQueue
from config import (
    WORKLOAD_OVERLOAD_THRESHOLD,
    WORKLOAD_UNDERLOAD_THRESHOLD,
    EMERGENCY_THRESHOLD
)

class BaristaScheduler:
    """Manages barista assignments with workload balancing"""
    
    def __init__(self, baristas: List[Barista]):
        self.baristas = baristas
        self.order_queue = OrderQueue()
    
    def get_available_baristas(self, current_time: datetime) -> List[Barista]:
        """Get all baristas currently available"""
        available = []
        for barista in self.baristas:
            # Check if barista should be available by now
            if current_time >= barista.available_at:
                # If they have a current order, complete it
                if barista.current_order:
                    barista.complete_order(current_time)
                available.append(barista)
        return available
    
    def calculate_workload_ratio(self, barista: Barista) -> float:
        """
        Calculate barista's workload ratio compared to average
        Returns: ratio where 1.0 = average, >1.0 = overloaded, <1.0 = underutilized
        """
        if not self.baristas:
            return 1.0
        
        avg_workload = sum(b.workload_minutes for b in self.baristas) / len(self.baristas)
        
        if avg_workload == 0:
            return 1.0
        
        return barista.workload_minutes / avg_workload
    
    def select_barista_for_order(self, order: Order, available_baristas: List[Barista]) -> Optional[Barista]:
        """
        Select the best barista for an order considering workload balance
        
        Strategy:
        - Emergency orders: assign to least busy barista
        - Complex orders: prefer underutilized baristas
        - Simple orders: can go to overloaded baristas for balance
        """
        if not available_baristas:
            return None
        
        # Sort by workload (ascending)
        sorted_baristas = sorted(available_baristas, key=lambda b: b.workload_minutes)
        
        # Emergency handling: always assign to least busy
        if order.wait_time_minutes >= EMERGENCY_THRESHOLD:
            return sorted_baristas[0]
        
        # For complex orders (>4 min), prefer underutilized baristas
        if order.total_prep_time >= 4:
            for barista in sorted_baristas:
                ratio = self.calculate_workload_ratio(barista)
                if ratio <= 1.0:  # At or below average
                    return barista
            # If all are overloaded, take least busy
            return sorted_baristas[0]
        
        # For simple orders (<4 min), help balance overloaded baristas
        for barista in sorted_baristas:
            ratio = self.calculate_workload_ratio(barista)
            if ratio >= WORKLOAD_OVERLOAD_THRESHOLD:
                return barista
        
        # Default: least busy barista
        return sorted_baristas[0]
    
    def assign_orders(self, current_time: datetime) -> List[tuple]:
        """
        Assign waiting orders to available baristas
        
        Returns: List of (barista, order) tuples representing assignments made
        """
        assignments = []
        
        # Get available baristas
        available_baristas = self.get_available_baristas(current_time)
        
        # Assign orders while we have both baristas and orders
        while available_baristas and not self.order_queue.is_empty():
            # Get highest priority order
            order = self.order_queue.get_highest_priority_order()
            if not order:
                break
            
            # Select best barista for this order
            barista = self.select_barista_for_order(order, available_baristas)
            if not barista:
                # Put order back if no barista available (shouldn't happen)
                self.order_queue.add_order(order)
                break
            
            # Make assignment
            barista.assign_order(order, current_time)
            assignments.append((barista, order))
            
            # Update skip counts for remaining orders
            self.order_queue.update_skip_counts(order)
            
            # Remove barista from available list
            available_baristas.remove(barista)
        
        return assignments
    
    def add_order(self, order: Order):
        """Add a new order to the queue"""
        self.order_queue.add_order(order)
    
    def get_queue_status(self) -> str:
        """Get current queue status"""
        return str(self.order_queue)
    
    def get_barista_status(self) -> str:
        """Get status of all baristas"""
        status = "Barista Status:\n"
        for barista in self.baristas:
            ratio = self.calculate_workload_ratio(barista)
            status += f"  {barista} (Workload: {ratio:.2f}x avg)\n"
        return status
    
    def get_workload_distribution(self) -> dict:
        """Calculate workload statistics"""
        workloads = [b.workload_minutes for b in self.baristas]
        avg = sum(workloads) / len(workloads) if workloads else 0
        
        # Calculate standard deviation
        variance = sum((w - avg) ** 2 for w in workloads) / len(workloads) if workloads else 0
        std_dev = variance ** 0.5
        
        return {
            'average': avg,
            'std_dev': std_dev,
            'min': min(workloads) if workloads else 0,
            'max': max(workloads) if workloads else 0,
            'balance_percentage': (1 - (std_dev / avg)) * 100 if avg > 0 else 100
        }
