"""
Streamlit utility functions for the Barista Queue System
Helper functions for charts, formatting, and session state management
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any


def format_time(minutes: float) -> str:
    """Format time in minutes to readable string.
    
    Args:
        minutes: Time in minutes
        
    Returns:
        Formatted time string
    """
    if minutes < 1:
        return f"{int(minutes * 60)}s"
    return f"{minutes:.1f}min"


def create_queue_chart(orders: List[Dict]) -> go.Figure:
    """Create a bar chart showing queue status.
    
    Args:
        orders: List of order dictionaries
        
    Returns:
        Plotly figure
    """
    if not orders:
        fig = go.Figure()
        fig.add_annotation(
            text="Queue is empty",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig
    
    df = pd.DataFrame(orders)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['order_number'],
        y=df['priority_score'],
        marker_color=df['priority_score'],
        marker_colorscale='Viridis',
        text=df['drink_name'],
        textposition='auto',
        hovertemplate='<b>Order #%{x}</b><br>' +
                      'Drink: %{text}<br>' +
                      'Priority: %{y:.2f}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title="Current Queue by Priority",
        xaxis_title="Order Number",
        yaxis_title="Priority Score",
        height=400
    )
    
    return fig


def create_barista_status_chart(baristas: List[Dict]) -> go.Figure:
    """Create a chart showing barista workload.
    
    Args:
        baristas: List of barista dictionaries
        
    Returns:
        Plotly figure
    """
    if not baristas:
        return go.Figure()
    
    df = pd.DataFrame(baristas)
    
    fig = go.Figure()
    
    # Add bars for total minutes worked
    fig.add_trace(go.Bar(
        name='Total Minutes',
        x=df['name'],
        y=df['total_minutes'],
        marker_color='#6F4E37'
    ))
    
    # Add bars for total orders
    fig.add_trace(go.Bar(
        name='Total Orders',
        x=df['name'],
        y=df['total_orders'],
        marker_color='#764ba2'
    ))
    
    fig.update_layout(
        title="Barista Workload",
        xaxis_title="Barista",
        yaxis_title="Count",
        barmode='group',
        height=400
    )
    
    return fig


def create_wait_time_distribution(orders: List[Dict]) -> go.Figure:
    """Create histogram of wait times.
    
    Args:
        orders: List of order dictionaries with wait_time
        
    Returns:
        Plotly figure
    """
    if not orders:
        return go.Figure()
    
    df = pd.DataFrame(orders)
    wait_times = df['wait_time'].dropna()
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=wait_times,
        nbinsx=20,
        marker_color='#6F4E37',
        opacity=0.7
    ))
    
    # Add vertical line for average
    avg_wait = wait_times.mean()
    fig.add_vline(
        x=avg_wait,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Avg: {avg_wait:.2f} min",
        annotation_position="top right"
    )
    
    # Add vertical line for 10-minute threshold
    fig.add_vline(
        x=10,
        line_dash="dash",
        line_color="orange",
        annotation_text="10 min threshold",
        annotation_position="top left"
    )
    
    fig.update_layout(
        title="Wait Time Distribution",
        xaxis_title="Wait Time (minutes)",
        yaxis_title="Number of Orders",
        height=400
    )
    
    return fig


def create_timeline_chart(events: List[Dict]) -> go.Figure:
    """Create timeline chart of events.
    
    Args:
        events: List of event dictionaries
        
    Returns:
        Plotly figure
    """
    if not events:
        return go.Figure()
    
    df = pd.DataFrame(events)
    
    # Color mapping for event types
    color_map = {
        'order_arrived': '#3498db',
        'order_assigned': '#2ecc71',
        'order_completed': '#27ae60',
        'barista_free': '#95a5a6'
    }
    
    df['color'] = df['event_type'].map(color_map).fillna('#95a5a6')
    
    fig = go.Figure()
    
    for event_type in df['event_type'].unique():
        df_type = df[df['event_type'] == event_type]
        fig.add_trace(go.Scatter(
            x=df_type['timestamp'],
            y=[event_type] * len(df_type),
            mode='markers',
            name=event_type.replace('_', ' ').title(),
            marker=dict(size=10, color=df_type['color'])
        ))
    
    fig.update_layout(
        title="Event Timeline",
        xaxis_title="Time (minutes)",
        yaxis_title="Event Type",
        height=400,
        showlegend=True
    )
    
    return fig


def create_performance_gauge(value: float, title: str, 
                            max_value: float = 100,
                            threshold_good: float = 80,
                            threshold_ok: float = 60) -> go.Figure:
    """Create a gauge chart for performance metrics.
    
    Args:
        value: Current value
        title: Gauge title
        max_value: Maximum value for gauge
        threshold_good: Threshold for good performance
        threshold_ok: Threshold for ok performance
        
    Returns:
        Plotly figure
    """
    # Determine color based on thresholds
    if value >= threshold_good:
        color = "green"
    elif value >= threshold_ok:
        color = "yellow"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, threshold_ok], 'color': "lightgray"},
                {'range': [threshold_ok, threshold_good], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': threshold_good
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig


def create_comparison_table(priority_metrics: Dict, fifo_metrics: Dict) -> pd.DataFrame:
    """Create comparison table between priority queue and FIFO.
    
    Args:
        priority_metrics: Metrics from priority queue simulation
        fifo_metrics: Metrics from FIFO simulation
        
    Returns:
        Pandas DataFrame
    """
    comparison_data = {
        'Metric': [
            'Average Wait Time',
            'Max Wait Time',
            'Timeout Rate',
            'Workload Balance',
            'Total Customers'
        ],
        'Priority Queue': [
            f"{priority_metrics.get('avg_wait_time', 0):.2f} min",
            f"{priority_metrics.get('max_wait_time', 0):.2f} min",
            f"{priority_metrics.get('timeout_rate', 0) * 100:.1f}%",
            f"{priority_metrics.get('workload_balance', 0) * 100:.1f}%",
            priority_metrics.get('total_customers', 0)
        ],
        'FIFO': [
            f"{fifo_metrics.get('avg_wait_time', 0):.2f} min",
            f"{fifo_metrics.get('max_wait_time', 0):.2f} min",
            f"{fifo_metrics.get('timeout_rate', 0) * 100:.1f}%",
            f"{fifo_metrics.get('workload_balance', 0) * 100:.1f}%",
            fifo_metrics.get('total_customers', 0)
        ]
    }
    
    return pd.DataFrame(comparison_data)


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'simulation_running' not in st.session_state:
        st.session_state.simulation_running = False
    
    if 'current_run_id' not in st.session_state:
        st.session_state.current_run_id = None
    
    if 'orders_submitted' not in st.session_state:
        st.session_state.orders_submitted = 0


def display_metric_card(title: str, value: str, delta: str = None, 
                       delta_color: str = "normal"):
    """Display a styled metric card.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Optional delta value
        delta_color: Color for delta (normal, inverse, off)
    """
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
        ">
            <h3 style="margin: 0; font-size: 1rem; opacity: 0.9;">{title}</h3>
            <p style="margin: 0.5rem 0 0 0; font-size: 2rem; font-weight: bold;">{value}</p>
            {f'<p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">{delta}</p>' if delta else ''}
        </div>
    """, unsafe_allow_html=True)


def get_status_emoji(status: str) -> str:
    """Get emoji for order status.
    
    Args:
        status: Order status
        
    Returns:
        Emoji string
    """
    status_map = {
        'pending': '⏳',
        'in_progress': '🔄',
        'completed': '✅',
        'timeout': '⚠️'
    }
    return status_map.get(status, '❓')


def format_customer_type(customer_type: str) -> str:
    """Format customer type with emoji.
    
    Args:
        customer_type: Customer type (NEW, REGULAR, GOLD)
        
    Returns:
        Formatted string with emoji
    """
    type_map = {
        'NEW': '🆕 New',
        'REGULAR': '👤 Regular',
        'GOLD': '⭐ Gold'
    }
    return type_map.get(customer_type, customer_type)
