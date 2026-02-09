# Utility functions

from datetime import datetime, timedelta
from typing import List

def format_time(dt: datetime) -> str:
    """Format datetime as HH:MM"""
    return dt.strftime("%H:%M")

def format_duration(minutes: float) -> str:
    """Format duration in minutes to readable string"""
    if minutes < 1:
        return f"{int(minutes * 60)}s"
    return f"{minutes:.1f}min"

def calculate_statistics(values: List[float]) -> dict:
    """Calculate basic statistics for a list of values"""
    if not values:
        return {
            'mean': 0,
            'min': 0,
            'max': 0,
            'std': 0
        }
    
    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    std = variance ** 0.5
    
    return {
        'mean': mean,
        'min': min(values),
        'max': max(values),
        'std': std
    }

def print_separator(char='=', length=60):
    """Print a separator line"""
    print(char * length)

def print_section_header(title: str):
    """Print a section header"""
    print_separator()
    print(f" {title}")
    print_separator()
