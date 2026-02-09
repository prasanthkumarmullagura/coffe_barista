# Simulation engine for Coffee Shop operations

import random
from datetime import datetime, timedelta
from typing import List
import numpy as np

from models import (
    Order, Barista, MenuItem, DrinkType, CustomerType, SimulationMetrics
)
from scheduler import BaristaScheduler
from config import (
    MENU_ITEMS, NUM_BARISTAS, CUSTOMER_ARRIVAL_RATE,
    OPERATING_HOURS
)

class OrderGenerator:
    """Generates random orders based on menu frequencies"""
    
    def __init__(self):
        self.menu_items = self._create_menu_items()
        self.drink_types = list(DrinkType)
        self.weights = [MENU_ITEMS[dt.name].frequency_percent for dt in self.drink_types]
    
    def _create_menu_items(self) -> dict:
        """Create MenuItem objects from config"""
        items = {}
        for drink_type in DrinkType:
            config = MENU_ITEMS[drink_type.name]
            items[drink_type] = MenuItem(
                drink_type=drink_type,
                prep_time_minutes=config.prep_time_minutes,
                price_inr=config.price_inr,
                frequency_percent=config.frequency_percent
            )
        return items
    
    def generate_order(self, arrival_time: datetime) -> Order:
        """Generate a random order"""
        # Select drink type based on frequency weights
        drink_type = random.choices(self.drink_types, weights=self.weights, k=1)[0]
        drink = self.menu_items[drink_type]
        
        # Determine customer type (70% regular, 20% new, 10% gold)
        customer_type = random.choices(
            [CustomerType.REGULAR, CustomerType.NEW, CustomerType.GOLD],
            weights=[70, 20, 10],
            k=1
        )[0]
        
        # Most orders are single drink, some are multiple
        num_drinks = random.choices([1, 2], weights=[85, 15], k=1)[0]
        drinks = [drink] if num_drinks == 1 else [drink, self._get_random_drink()]
        
        return Order(
            drinks=drinks,
            customer_type=customer_type,
            arrival_time=arrival_time
        )
    
    def _get_random_drink(self) -> MenuItem:
        """Get a random drink for multi-drink orders"""
        drink_type = random.choices(self.drink_types, weights=self.weights, k=1)[0]
        return self.menu_items[drink_type]

class CoffeeShopSimulation:
    """Simulates coffee shop operations during rush hour"""
    
    def __init__(self, num_baristas: int = NUM_BARISTAS, arrival_rate: float = CUSTOMER_ARRIVAL_RATE):
        self.num_baristas = num_baristas
        self.arrival_rate = arrival_rate  # λ for Poisson
        self.order_generator = OrderGenerator()
        self.metrics = SimulationMetrics()
        
        # Simulation state
        self.current_time = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
        
        # Initialize baristas with simulation start time
        self.baristas = [
            Barista(
                barista_id=f"B{i+1}", 
                name=f"Barista {i+1}",
                available_at=self.current_time  # Start available at simulation start
            )
            for i in range(num_baristas)
        ]
        
        # Initialize scheduler
        self.scheduler = BaristaScheduler(self.baristas)
        
        self.all_orders: List[Order] = []
    
    def generate_arrival_times(self, duration_minutes: int) -> List[datetime]:
        """
        Generate customer arrival times using Poisson process
        
        Args:
            duration_minutes: Total simulation duration in minutes
        
        Returns:
            List of arrival times
        """
        arrivals = []
        current_minute = 0
        
        while current_minute < duration_minutes:
            # Poisson: time between arrivals is exponentially distributed
            inter_arrival_time = np.random.exponential(1.0 / self.arrival_rate)
            current_minute += inter_arrival_time
            
            if current_minute < duration_minutes:
                arrival_time = self.current_time + timedelta(minutes=current_minute)
                arrivals.append(arrival_time)
        
        return arrivals
    
    def run(self, duration_minutes: int = OPERATING_HOURS['duration_minutes'], 
            verbose: bool = False) -> SimulationMetrics:
        """
        Run the simulation
        
        Args:
            duration_minutes: How long to simulate (default: 180 min = 3 hours)
            verbose: Whether to print detailed progress
        
        Returns:
            SimulationMetrics with performance data
        """
        # Generate all customer arrivals
        arrival_times = self.generate_arrival_times(duration_minutes)
        self.metrics.total_orders = len(arrival_times)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"COFFEE SHOP SIMULATION - {len(arrival_times)} customers expected")
            print(f"{'='*60}\n")
        
        # Create event timeline (arrivals + completions)
        events = [(time, 'arrival', None) for time in arrival_times]
        events.sort()
        
        # Process events
        event_idx = 0
        while event_idx < len(events):
            event_time, event_type, event_data = events[event_idx]
            self.current_time = event_time
            
            if event_type == 'arrival':
                # New customer arrives
                order = self.order_generator.generate_order(event_time)
                self.all_orders.append(order)
                self.scheduler.add_order(order)
                
                if verbose:
                    print(f"[{event_time.strftime('%H:%M')}] NEW: {order}")
            
            # Try to assign orders to available baristas
            assignments = self.scheduler.assign_orders(self.current_time)
            
            if verbose and assignments:
                for barista, order in assignments:
                    print(f"[{event_time.strftime('%H:%M')}] ASSIGNED: {order} to {barista.name}")
            
            # Schedule completion events for newly assigned orders
            for barista, order in assignments:
                completion_time = barista.available_at
                # Insert completion event in chronological order
                completion_event = (completion_time, 'completion', barista)
                # Find insertion point
                insert_idx = event_idx + 1
                while insert_idx < len(events) and events[insert_idx][0] < completion_time:
                    insert_idx += 1
                events.insert(insert_idx, completion_event)
            
            # Handle completion events
            if event_type == 'completion':
                barista = event_data
                if barista.current_order:
                    completed_order = barista.current_order
                    barista.complete_order(self.current_time)
                    if verbose:
                        print(f"[{event_time.strftime('%H:%M')}] COMPLETED: Order-{completed_order.order_id} by {barista.name}")
            
            event_idx += 1
        
        # Simulation end: complete any remaining orders in progress
        end_time = self.current_time + timedelta(minutes=30)  # 30 min buffer
        for barista in self.baristas:
            if barista.current_order:
                barista.complete_order(barista.available_at)
        
        # Calculate final metrics
        for order in self.all_orders:
            if order.completion_time:
                self.metrics.update_with_order(order)
        
        if verbose:
            print(f"\n{'='*60}")
            print("SIMULATION COMPLETE")
            print(f"{'='*60}")
            print(self.metrics)
            print(self.scheduler.get_barista_status())
            workload = self.scheduler.get_workload_distribution()
            print(f"\nWorkload Balance: {workload['balance_percentage']:.1f}%")
            print(f"Std Dev: {workload['std_dev']:.2f} minutes")
        
        return self.metrics
    
    def get_summary(self) -> dict:
        """Get summary statistics"""
        workload = self.scheduler.get_workload_distribution()
        
        return {
            'total_orders': self.metrics.total_orders,
            'completed_orders': self.metrics.completed_orders,
            'avg_wait_time': self.metrics.average_wait_time,
            'max_wait_time': self.metrics.max_wait_time,
            'timeout_rate': self.metrics.timeout_rate,
            'fairness_violation_rate': self.metrics.fairness_violation_rate,
            'workload_balance': workload['balance_percentage'],
            'workload_std_dev': workload['std_dev']
        }

def run_monte_carlo(num_runs: int = 1000, verbose: bool = False) -> dict:
    """
    Run Monte Carlo simulation to get statistical performance
    
    Args:
        num_runs: Number of simulations to run
        verbose: Whether to print progress
    
    Returns:
        Dictionary with aggregated statistics
    """
    results = {
        'avg_wait_times': [],
        'max_wait_times': [],
        'timeout_rates': [],
        'workload_balances': []
    }
    
    for i in range(num_runs):
        if verbose and (i + 1) % 100 == 0:
            print(f"Completed {i+1}/{num_runs} simulations...")
        
        sim = CoffeeShopSimulation()
        metrics = sim.run(verbose=False)
        summary = sim.get_summary()
        
        results['avg_wait_times'].append(summary['avg_wait_time'])
        results['max_wait_times'].append(summary['max_wait_time'])
        results['timeout_rates'].append(summary['timeout_rate'])
        results['workload_balances'].append(summary['workload_balance'])
    
    # Calculate statistics
    avg_stats = {
        'avg_wait_time_mean': np.mean(results['avg_wait_times']),
        'avg_wait_time_std': np.std(results['avg_wait_times']),
        'max_wait_time_mean': np.mean(results['max_wait_times']),
        'timeout_rate_mean': np.mean(results['timeout_rates']),
        'timeout_rate_std': np.std(results['timeout_rates']),
        'workload_balance_mean': np.mean(results['workload_balances']),
        'workload_balance_std': np.std(results['workload_balances'])
    }
    
    return avg_stats
