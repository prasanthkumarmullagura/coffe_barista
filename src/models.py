# Core data models for the Coffee Shop Barista Queuing System

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
import uuid

class DrinkType(Enum):
    """Enumeration of available drink types"""
    COLD_BREW = "Cold Brew"
    ESPRESSO = "Espresso"
    AMERICANO = "Americano"
    CAPPUCCINO = "Cappuccino"
    LATTE = "Latte"
    SPECIALTY = "Specialty (Mocha)"

class CustomerType(Enum):
    """Customer loyalty status"""
    NEW = "New"
    REGULAR = "Regular"
    GOLD = "Gold"

@dataclass
class MenuItem:
    """Represents a menu item with all its properties"""
    drink_type: DrinkType
    prep_time_minutes: int
    price_inr: int
    frequency_percent: int
    
    def __str__(self):
        return f"{self.drink_type.value} (₹{self.price_inr}, {self.prep_time_minutes}min)"

@dataclass
class Order:
    """Represents a customer order"""
    order_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    drinks: List[MenuItem] = field(default_factory=list)
    customer_type: CustomerType = CustomerType.REGULAR
    arrival_time: datetime = field(default_factory=datetime.now)
    assigned_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    assigned_barista_id: Optional[str] = None
    priority_score: float = 0.0
    skip_count: int = 0  # How many later arrivals have been served first
    
    @property
    def total_prep_time(self) -> int:
        """Total preparation time for all drinks in the order"""
        return sum(drink.prep_time_minutes for drink in self.drinks)
    
    @property
    def total_price(self) -> int:
        """Total price of the order"""
        return sum(drink.price_inr for drink in self.drinks)
    
    @property
    def wait_time_minutes(self) -> float:
        """Current wait time in minutes"""
        if self.completion_time:
            end_time = self.completion_time
        elif self.assigned_time:
            end_time = self.assigned_time
        else:
            end_time = datetime.now()
        return (end_time - self.arrival_time).total_seconds() / 60
    
    @property
    def is_timeout_risk(self) -> bool:
        """Check if order is approaching timeout"""
        return self.wait_time_minutes > 8
    
    @property
    def has_violated_constraint(self) -> bool:
        """Check if order has violated max wait time"""
        return self.wait_time_minutes > 10
    
    def __str__(self):
        drinks_str = ", ".join([d.drink_type.value for d in self.drinks])
        return f"Order-{self.order_id} ({drinks_str}) - {self.total_prep_time}min"

@dataclass
class Barista:
    """Represents a barista"""
    barista_id: str
    name: str
    current_order: Optional[Order] = None
    total_orders_completed: int = 0
    total_minutes_worked: float = 0.0
    available_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_available(self) -> bool:
        """Check if barista is currently available"""
        return self.current_order is None
    
    @property
    def workload_minutes(self) -> float:
        """Total workload in minutes"""
        return self.total_minutes_worked
    
    def assign_order(self, order: Order, current_time: datetime):
        """Assign an order to this barista"""
        self.current_order = order
        order.assigned_time = current_time
        order.assigned_barista_id = self.barista_id
        self.available_at = current_time + timedelta(minutes=order.total_prep_time)
    
    def complete_order(self, current_time: datetime):
        """Mark current order as complete"""
        if self.current_order:
            self.current_order.completion_time = current_time
            self.total_minutes_worked += self.current_order.total_prep_time
            self.total_orders_completed += 1
            self.current_order = None
    
    def __str__(self):
        status = "Busy" if not self.is_available else "Available"
        return f"{self.name} ({status}) - {self.total_orders_completed} orders, {self.total_minutes_worked:.1f}min worked"

@dataclass
class SimulationMetrics:
    """Tracks performance metrics during simulation"""
    total_orders: int = 0
    completed_orders: int = 0
    total_wait_time: float = 0.0
    max_wait_time: float = 0.0
    timeout_count: int = 0  # Orders that waited > 10 min
    fairness_violations: int = 0  # Orders where skip_count > 3
    fairness_justified: int = 0  # Violations where skipped orders were quick
    
    @property
    def average_wait_time(self) -> float:
        """Calculate average wait time"""
        return self.total_wait_time / self.completed_orders if self.completed_orders > 0 else 0.0
    
    @property
    def timeout_rate(self) -> float:
        """Percentage of orders that timed out"""
        return (self.timeout_count / self.completed_orders * 100) if self.completed_orders > 0 else 0.0
    
    @property
    def fairness_violation_rate(self) -> float:
        """Percentage of fairness violations"""
        return (self.fairness_violations / self.completed_orders * 100) if self.completed_orders > 0 else 0.0
    
    def update_with_order(self, order: Order):
        """Update metrics with a completed order"""
        self.completed_orders += 1
        wait_time = order.wait_time_minutes
        self.total_wait_time += wait_time
        self.max_wait_time = max(self.max_wait_time, wait_time)
        
        if order.has_violated_constraint:
            self.timeout_count += 1
        
        if order.skip_count > 3:
            self.fairness_violations += 1
    
    def __str__(self):
        return f"""
Simulation Metrics:
  Total Orders: {self.total_orders}
  Completed Orders: {self.completed_orders}
  Average Wait Time: {self.average_wait_time:.2f} minutes
  Max Wait Time: {self.max_wait_time:.2f} minutes
  Timeout Rate: {self.timeout_rate:.2f}%
  Fairness Violations: {self.fairness_violation_rate:.2f}%
"""
