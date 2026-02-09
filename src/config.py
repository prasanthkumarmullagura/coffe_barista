# Configuration file for Coffee Shop Barista Queuing System

from enum import Enum
from dataclasses import dataclass

# Operating Parameters
OPERATING_HOURS = {
    'start': 7,  # 7 AM
    'end': 10,   # 10 AM
    'duration_minutes': 180  # 3 hours
}

# Staff Configuration
NUM_BARISTAS = 3

# Customer Arrival Pattern (Poisson distribution)
CUSTOMER_ARRIVAL_RATE = 1.4  # λ = 1.4 customers per minute
EXPECTED_CUSTOMERS = 250  # Average during rush

# Wait Time Constraints
MAX_WAIT_TIME_MINUTES = 10  # Hard constraint
REGULAR_CUSTOMER_TOLERANCE = 10  # minutes
NEW_CUSTOMER_TOLERANCE = 8  # minutes
EMERGENCY_THRESHOLD = 8  # Trigger emergency handling

# Priority Scoring Weights
PRIORITY_WEIGHTS = {
    'wait_time': 0.40,      # 40%
    'complexity': 0.25,     # 25%
    'loyalty': 0.10,        # 10%
    'urgency': 0.25         # 25%
}

# Fairness Parameters
MAX_SKIP_COUNT = 3  # Max people who can be served ahead
PRIORITY_UPDATE_INTERVAL = 30  # seconds

# Workload Balancing Thresholds
WORKLOAD_OVERLOAD_THRESHOLD = 1.2  # 120% of average
WORKLOAD_UNDERLOAD_THRESHOLD = 0.8  # 80% of average

# Menu Configuration
@dataclass
class DrinkConfig:
    name: str
    prep_time_minutes: int
    frequency_percent: int
    price_inr: int

MENU_ITEMS = {
    'COLD_BREW': DrinkConfig('Cold Brew', 1, 25, 120),
    'ESPRESSO': DrinkConfig('Espresso', 2, 20, 150),
    'AMERICANO': DrinkConfig('Americano', 2, 15, 140),
    'CAPPUCCINO': DrinkConfig('Cappuccino', 4, 20, 180),
    'LATTE': DrinkConfig('Latte', 4, 12, 200),
    'SPECIALTY': DrinkConfig('Specialty (Mocha)', 6, 8, 250)
}

# Validate frequencies sum to 100%
assert sum(item.frequency_percent for item in MENU_ITEMS.values()) == 100, \
    "Menu item frequencies must sum to 100%"
