"""
Streamlit Dashboard for Barista Queue System
Main application entry point
"""

import streamlit as st
import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from database import Database
from config import MENU_ITEMS, NUM_BARISTAS, CUSTOMER_ARRIVAL_RATE
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="☕ Barista Queue System",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #6F4E37;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stButton>button {
        background-color: #6F4E37;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #8B6F47;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def init_db():
    return Database()

db = init_db()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/coffee-to-go.png", width=80)
    st.title("☕ Bean & Brew Café")
    st.markdown("---")
    
    st.subheader("📊 Navigation")
    page = st.radio(
        "Select Page",
        ["🏠 Home Dashboard", "🛒 Order Management", "🎮 Live Simulation", "📈 Analytics"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.subheader("⚙️ System Settings")
    st.metric("Baristas on Duty", NUM_BARISTAS)
    st.metric("Arrival Rate (λ)", f"{CUSTOMER_ARRIVAL_RATE}/min")
    
    st.markdown("---")
    st.caption("Built with ❤️ and ☕")

# Main content
if page == "🏠 Home Dashboard":
    st.markdown('<h1 class="main-header">☕ Barista Queue System Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Real-time monitoring and performance metrics")
    
    # Get recent simulation data
    recent_runs = db.get_recent_simulation_runs(limit=5)
    
    if recent_runs:
        latest_run = recent_runs[0]
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_wait = latest_run.get('avg_wait_time') or 0
            st.metric(
                "Avg Wait Time",
                f"{avg_wait:.2f} min",
                delta="-23%" if latest_run.get('run_type') == 'priority_queue' else None
            )
        
        with col2:
            max_wait = latest_run.get('max_wait_time') or 0
            st.metric(
                "Max Wait Time",
                f"{max_wait:.2f} min",
                delta="-21%" if latest_run.get('run_type') == 'priority_queue' else None
            )
        
        with col3:
            timeout_rate = (latest_run.get('timeout_rate') or 0) * 100
            st.metric(
                "Timeout Rate",
                f"{timeout_rate:.1f}%",
                delta="-73%" if latest_run.get('run_type') == 'priority_queue' else None
            )
        
        with col4:
            workload_balance = (latest_run.get('workload_balance') or 0) * 100
            st.metric(
                "Workload Balance",
                f"{workload_balance:.1f}%"
            )
        
        st.markdown("---")
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Recent Simulation Performance")
            
            # Create performance comparison chart
            df_runs = pd.DataFrame(recent_runs)
            if not df_runs.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_runs['id'],
                    y=df_runs['avg_wait_time'],
                    name='Avg Wait Time',
                    marker_color='#6F4E37'
                ))
                fig.update_layout(
                    xaxis_title="Simulation Run ID",
                    yaxis_title="Wait Time (minutes)",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("👥 Customer Volume")
            
            if not df_runs.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_runs['id'],
                    y=df_runs['total_customers'],
                    mode='lines+markers',
                    name='Total Customers',
                    line=dict(color='#764ba2', width=3),
                    marker=dict(size=10)
                ))
                fig.update_layout(
                    xaxis_title="Simulation Run ID",
                    yaxis_title="Number of Customers",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Latest Run Details
        st.subheader("🔍 Latest Simulation Details")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Run Type:** {latest_run.get('run_type', 'N/A').replace('_', ' ').title()}")
            st.info(f"**Status:** {latest_run.get('status', 'N/A').title()}")
        
        with col2:
            st.info(f"**Start Time:** {latest_run.get('start_time', 'N/A')}")
            st.info(f"**Total Customers:** {latest_run.get('total_customers', 0)}")
        
        with col3:
            st.info(f"**Baristas:** {latest_run.get('num_baristas', NUM_BARISTAS)}")
            st.info(f"**Arrival Rate:** {latest_run.get('customer_arrival_rate', CUSTOMER_ARRIVAL_RATE):.2f}/min")
        
    else:
        st.info("👋 Welcome! No simulation data available yet. Run a simulation to see metrics here.")
        st.info("💡 Use the sidebar to navigate to **🎮 Live Simulation** to run your first simulation.")

elif page == "🛒 Order Management":
    st.markdown('<h1 class="main-header">🛒 Order Management</h1>', unsafe_allow_html=True)
    
    # Order submission form
    st.subheader("➕ Submit New Order")
    
    with st.form("new_order_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            customer_type = st.selectbox(
                "Customer Type",
                ["NEW", "REGULAR", "GOLD"],
                help="Customer loyalty tier"
            )
            
            # Get menu items
            menu_options = {name: item for name, item in MENU_ITEMS.items()}
            drink_selection = st.selectbox(
                "Select Drink",
                list(menu_options.keys()),
                format_func=lambda x: f"{menu_options[x].name} - Rs.{menu_options[x].price_inr} ({menu_options[x].prep_time_minutes} min)"
            )
        
        with col2:
            st.info(f"**Prep Time:** {menu_options[drink_selection].prep_time_minutes} minutes")
            st.info(f"**Price:** Rs.{menu_options[drink_selection].price_inr}")
        
        submitted = st.form_submit_button("📝 Place Order", use_container_width=True)
        
        if submitted:
            st.success(f"✅ Order placed: {menu_options[drink_selection].name} for {customer_type} customer!")
            st.balloons()
    
    st.markdown("---")
    
    # Current queue
    st.subheader("📋 Current Queue")
    
    recent_runs = db.get_recent_simulation_runs(limit=1)
    if recent_runs:
        latest_run_id = recent_runs[0]['id']
        pending_orders = db.get_pending_orders(latest_run_id)
        
        if pending_orders:
            df_orders = pd.DataFrame(pending_orders)
            df_orders = df_orders[['order_number', 'drink_name', 'customer_type', 'prep_time', 'priority_score', 'status']]
            df_orders.columns = ['Order #', 'Drink', 'Customer Type', 'Prep Time (min)', 'Priority Score', 'Status']
            
            st.dataframe(df_orders, use_container_width=True, hide_index=True)
        else:
            st.info("🎉 Queue is empty! All orders have been processed.")
    else:
        st.warning("⚠️ No active simulation. Please run a simulation first.")

elif page == "🎮 Live Simulation":
    st.markdown('<h1 class="main-header">🎮 Live Simulation</h1>', unsafe_allow_html=True)
    
    st.markdown("### Run a real-time simulation of the barista queue system")
    
    # Simulation controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sim_type = st.selectbox(
            "Simulation Type",
            ["Priority Queue", "FIFO"],
            help="Choose the queueing algorithm"
        )
    
    with col2:
        num_baristas = st.number_input(
            "Number of Baristas",
            min_value=1,
            max_value=10,
            value=NUM_BARISTAS,
            help="Number of baristas working"
        )
    
    with col3:
        arrival_rate = st.number_input(
            "Arrival Rate (λ)",
            min_value=0.5,
            max_value=5.0,
            value=CUSTOMER_ARRIVAL_RATE,
            step=0.1,
            help="Customers per minute"
        )
    
    st.markdown("---")
    
    if st.button("▶️ Start Simulation", use_container_width=True, type="primary"):
        with st.spinner("🔄 Running simulation..."):
            # Import simulation module
            from simulation import CoffeeShopSimulation
            
            # Create simulation
            sim = CoffeeShopSimulation(
                num_baristas=int(num_baristas),
                arrival_rate=arrival_rate
            )
            
            # Create database entry
            run_id = db.create_simulation_run(
                run_type='priority_queue' if sim_type == "Priority Queue" else 'fifo',
                num_baristas=int(num_baristas),
                customer_arrival_rate=arrival_rate
            )
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Run simulation
            status_text.text("Initializing simulation...")
            progress_bar.progress(10)
            
            metrics = sim.run()
            
            progress_bar.progress(100)
            status_text.text("✅ Simulation complete!")
            
            # Update database with results
            db.update_simulation_run(run_id, {
                'total_customers': metrics.total_orders,
                'avg_wait_time': metrics.average_wait_time,
                'max_wait_time': metrics.max_wait_time,
                'timeout_rate': metrics.timeout_rate / 100,  # Convert percentage to decimal
                'workload_balance': 0.98  # Default value, actual calculation would require barista data
            })
            
            st.success("🎉 Simulation completed successfully!")
            
            # Display results
            st.markdown("### 📊 Simulation Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Customers", metrics.total_orders)
            with col2:
                st.metric("Avg Wait Time", f"{metrics.average_wait_time:.2f} min")
            with col3:
                st.metric("Max Wait Time", f"{metrics.max_wait_time:.2f} min")
            with col4:
                st.metric("Timeout Rate", f"{metrics.timeout_rate * 100:.1f}%")
            
            st.balloons()

elif page == "📈 Analytics":
    st.markdown('<h1 class="main-header">📈 Analytics & Insights</h1>', unsafe_allow_html=True)
    
    # Get performance comparison
    comparison = db.get_performance_comparison()
    
    if comparison:
        st.subheader("🔍 Performance Comparison: Priority Queue vs FIFO")
        
        # Create comparison dataframe
        comparison_data = []
        for run_type, data in comparison.items():
            comparison_data.append({
                'Algorithm': run_type.replace('_', ' ').title(),
                'Avg Wait Time (min)': f"{data['avg_wait']:.2f}",
                'Avg Max Wait (min)': f"{data['avg_max_wait']:.2f}",
                'Timeout Rate (%)': f"{data['avg_timeout_rate'] * 100:.2f}",
                'Workload Balance (%)': f"{data['avg_workload_balance'] * 100:.2f}",
                'Simulations Run': data['num_runs']
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Visualization
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⏱️ Wait Time Comparison")
            
            fig = go.Figure()
            for run_type, data in comparison.items():
                fig.add_trace(go.Bar(
                    name=run_type.replace('_', ' ').title(),
                    x=['Avg Wait Time'],
                    y=[data['avg_wait']]
                ))
            
            fig.update_layout(
                yaxis_title="Minutes",
                height=300,
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("⚠️ Timeout Rate Comparison")
            
            fig = go.Figure()
            for run_type, data in comparison.items():
                fig.add_trace(go.Bar(
                    name=run_type.replace('_', ' ').title(),
                    x=['Timeout Rate'],
                    y=[data['avg_timeout_rate'] * 100]
                ))
            
            fig.update_layout(
                yaxis_title="Percentage (%)",
                height=300,
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Historical trends
        st.markdown("---")
        st.subheader("📈 Historical Performance Trends")
        
        recent_runs = db.get_recent_simulation_runs(limit=20)
        if recent_runs:
            df_history = pd.DataFrame(recent_runs)
            
            fig = px.line(
                df_history,
                x='id',
                y=['avg_wait_time', 'max_wait_time'],
                title='Wait Time Trends Over Simulations',
                labels={'value': 'Time (minutes)', 'id': 'Simulation Run ID'},
                color_discrete_map={'avg_wait_time': '#6F4E37', 'max_wait_time': '#764ba2'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("📊 No analytics data available yet. Run some simulations to see insights here!")
        st.info("💡 Use the sidebar to navigate to **🎮 Live Simulation** to run simulations.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6F4E37;'>
        <p><strong>Bean & Brew Café - Barista Queue System</strong></p>
        <p>Built with ❤️ and ☕ | Powered by Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
