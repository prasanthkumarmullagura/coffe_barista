# 🚀 Quick Start Guide - Barista Queue System

## Installation

1. **Navigate to the project directory:**
   ```bash
   cd "d:\HCL Training\Coffe_shop\barista-queue-system"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Web Dashboard

**Launch the Streamlit dashboard:**
```bash
streamlit run app.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

## Features

### 🏠 Home Dashboard
- View real-time metrics and performance
- Monitor queue status
- See barista workload

### 🛒 Order Management
- Submit new coffee orders
- View current queue
- Track order priorities

### 🎮 Live Simulation
- Run simulations with custom settings
- Compare Priority Queue vs FIFO
- Adjust parameters (baristas, arrival rate)

### 📈 Analytics
- View historical performance
- Compare algorithms
- Analyze trends

## Database

The system uses SQLite database (`barista_queue.db`) to store:
- Simulation runs
- Orders and their status
- Barista performance
- Metrics and events

The database is created automatically on first run.

## Troubleshooting

**Port already in use:**
```bash
streamlit run app.py --server.port 8502
```

**Dependencies not found:**
```bash
pip install --upgrade -r requirements.txt
```

**Database issues:**
Delete `barista_queue.db` and restart the app to create a fresh database.

## Next Steps

1. Run your first simulation in the Live Simulation page
2. Explore the analytics to see performance comparisons
3. Submit custom orders in Order Management
4. Review historical data in Analytics

Enjoy your coffee shop queue system! ☕
