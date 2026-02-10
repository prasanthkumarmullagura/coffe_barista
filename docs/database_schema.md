# Database Schema Documentation

## Overview

The Barista Queue System uses SQLite for data persistence. The database (`barista_queue.db`) is automatically created on first run.

## Tables

### simulation_runs
Stores metadata and metrics for each simulation execution.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| run_type | TEXT | Algorithm type ('priority_queue' or 'fifo') |
| start_time | TIMESTAMP | Simulation start time |
| end_time | TIMESTAMP | Simulation completion time |
| num_baristas | INTEGER | Number of baristas in simulation |
| customer_arrival_rate | REAL | Lambda for Poisson arrival (customers/min) |
| total_customers | INTEGER | Total customers served |
| avg_wait_time | REAL | Average wait time in minutes |
| max_wait_time | REAL | Maximum wait time in minutes |
| timeout_rate | REAL | Percentage of customers exceeding 10 min |
| workload_balance | REAL | Workload balance metric (0-1) |
| status | TEXT | 'running' or 'completed' |

### orders
Stores all order details and status.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| simulation_run_id | INTEGER | Foreign key to simulation_runs |
| order_number | INTEGER | Sequential order number |
| customer_type | TEXT | 'NEW', 'REGULAR', or 'GOLD' |
| drink_type | TEXT | Menu item key (e.g., 'COLD_BREW') |
| drink_name | TEXT | Display name of drink |
| prep_time | REAL | Preparation time in minutes |
| price | REAL | Price in INR |
| arrival_time | REAL | Time customer arrived (minutes) |
| start_time | REAL | Time order started (minutes) |
| completion_time | REAL | Time order completed (minutes) |
| wait_time | REAL | Total wait time (minutes) |
| assigned_barista_id | INTEGER | ID of assigned barista |
| priority_score | REAL | Calculated priority score |
| skip_count | INTEGER | Number of orders served ahead |
| status | TEXT | 'pending', 'in_progress', or 'completed' |

### baristas
Tracks barista workload and availability.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| simulation_run_id | INTEGER | Foreign key to simulation_runs |
| barista_id | INTEGER | Barista identifier (1, 2, 3, ...) |
| name | TEXT | Barista name |
| total_orders | INTEGER | Total orders completed |
| total_minutes | REAL | Total time spent on orders |
| is_busy | INTEGER | 1 if busy, 0 if available |
| current_order_id | INTEGER | ID of current order (if busy) |
| available_at | REAL | Time when barista becomes free |

### metrics_snapshots
Time-series performance data for trend analysis.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| simulation_run_id | INTEGER | Foreign key to simulation_runs |
| timestamp | REAL | Snapshot time (minutes) |
| queue_length | INTEGER | Number of pending orders |
| avg_wait_time | REAL | Average wait time at this point |
| orders_completed | INTEGER | Orders completed so far |
| orders_pending | INTEGER | Orders still pending |
| barista_utilization | TEXT | JSON object with barista stats |

### events
Event log for debugging and detailed analysis.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| simulation_run_id | INTEGER | Foreign key to simulation_runs |
| timestamp | REAL | Event time (minutes) |
| event_type | TEXT | Type of event (e.g., 'order_arrived') |
| order_id | INTEGER | Related order ID (optional) |
| barista_id | INTEGER | Related barista ID (optional) |
| details | TEXT | Additional event details |

## Database Operations

### Creating a Simulation Run
```python
from database import Database

db = Database()
run_id = db.create_simulation_run(
    run_type='priority_queue',
    num_baristas=3,
    customer_arrival_rate=1.4
)
```

### Inserting an Order
```python
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
```

### Querying Data
```python
# Get all orders for a simulation
orders = db.get_orders_by_simulation(run_id)

# Get pending orders
pending = db.get_pending_orders(run_id)

# Get barista status
baristas = db.get_baristas_by_simulation(run_id)

# Get performance comparison
comparison = db.get_performance_comparison()
```

## Data Persistence

- Database file: `barista_queue.db` (created automatically)
- All simulation runs are saved permanently
- Historical data available for analytics
- Event logging for debugging

## Maintenance

### Backup Database
```bash
# Windows
copy barista_queue.db barista_queue_backup.db

# Linux/Mac
cp barista_queue.db barista_queue_backup.db
```

### Reset Database
```bash
# Delete the database file to start fresh
del barista_queue.db  # Windows
rm barista_queue.db   # Linux/Mac
```

The database will be recreated automatically on next run.
