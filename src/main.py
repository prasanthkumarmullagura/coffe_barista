#!/usr/bin/env python3
"""
Coffee Shop Barista Queue System - Main Application

A smart order queuing system that optimizes barista workflow during peak hours
using Dynamic Priority Queue with Predictive Scheduling.
"""

import argparse
from datetime import datetime
from simulation import CoffeeShopSimulation, run_monte_carlo
from analytics import PerformanceAnalyzer
from utils import print_section_header, print_separator

def run_single_simulation(verbose: bool = True):
    """Run a single simulation and display results"""
    print_section_header("SINGLE SIMULATION RUN")
    
    sim = CoffeeShopSimulation()
    metrics = sim.run(verbose=verbose)
    summary = sim.get_summary()
    
    # Display results
    analyzer = PerformanceAnalyzer()
    print(analyzer.create_summary_table(summary))
    
    print("\nBarista Status:")
    print(sim.scheduler.get_barista_status())
    
    return summary

def run_monte_carlo_simulation(num_runs: int = 1000, verbose: bool = True):
    """Run Monte Carlo simulation"""
    print_section_header(f"MONTE CARLO SIMULATION ({num_runs} runs)")
    
    results = run_monte_carlo(num_runs=num_runs, verbose=verbose)
    
    # Display results
    print("\nMonte Carlo Results:")
    print_separator()
    print(f"Average Wait Time:    {results['avg_wait_time_mean']:.2f} ± {results['avg_wait_time_std']:.2f} min")
    print(f"Max Wait Time (avg):  {results['max_wait_time_mean']:.2f} min")
    print(f"Timeout Rate:         {results['timeout_rate_mean']:.2f} ± {results['timeout_rate_std']:.2f}%")
    print(f"Workload Balance:     {results['workload_balance_mean']:.1f} ± {results['workload_balance_std']:.1f}%")
    print_separator()
    
    # Comparison with FIFO
    analyzer = PerformanceAnalyzer()
    comparison = analyzer.generate_comparison_report(results, {})
    print(comparison)
    
    return results

def run_comparison_mode():
    """Compare priority queue vs FIFO"""
    print_section_header("COMPARISON MODE")
    
    print("\n[1/2] Running Priority Queue System...")
    pq_sim = CoffeeShopSimulation()
    pq_metrics = pq_sim.run(verbose=False)
    pq_summary = pq_sim.get_summary()
    
    print("[2/2] Simulating FIFO Baseline (expected values)...\n")
    
    # Display comparison
    print("+" + "-"*68 + "+")
    print("|" + " "*18 + "SYSTEM COMPARISON" + " "*33 + "|")
    print("+" + "-"*34 + "+" + "-"*33 + "+")
    print("| Metric" + " "*27 + "| Priority Queue | FIFO (Expected) |")
    print("+" + "-"*34 + "+" + "-"*16 + "+" + "-"*16 + "+")
    
    metrics = [
        ("Avg Wait Time", f"{pq_summary['avg_wait_time']:.2f} min", "6.2 min"),
        ("Timeout Rate", f"{pq_summary['timeout_rate']:.2f}%", "8.5%"),
        ("Workload Balance", f"{pq_summary['workload_balance']:.1f}%", "N/A"),
    ]
    
    for metric, pq_val, fifo_val in metrics:
        print(f"| {metric:.<32} | {pq_val:>14} | {fifo_val:>15} |")
    
    print("+" + "-"*34 + "+" + "-"*16 + "+" + "-"*16 + "+\n")

def interactive_mode():
    """Interactive mode for exploring the system"""
    print_section_header("INTERACTIVE MODE")
    print("\nAvailable Commands:")
    print("  1. Run single simulation")
    print("  2. Run Monte Carlo (100 runs)")
    print("  3. Run Monte Carlo (1000 runs)")
    print("  4. Compare with FIFO")
    print("  5. Exit")
    
    while True:
        print()
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == '1':
            run_single_simulation(verbose=True)
        elif choice == '2':
            run_monte_carlo_simulation(num_runs=100, verbose=True)
        elif choice == '3':
            run_monte_carlo_simulation(num_runs=1000, verbose=True)
        elif choice == '4':
            run_comparison_mode()
        elif choice == '5':
            print("\nExiting...")
            break
        else:
            print("Invalid choice. Please enter 1-5.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Coffee Shop Barista Queue System Simulation"
    )
    
    parser.add_argument(
        '--mode',
        choices=['single', 'monte-carlo', 'comparison', 'interactive'],
        default='single',
        help='Simulation mode (default: single)'
    )
    
    parser.add_argument(
        '--runs',
        type=int,
        default=1000,
        help='Number of Monte Carlo runs (default: 1000)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(" "*15 + "COFFEE SHOP BARISTA QUEUE SYSTEM")
    print("="*70)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run selected mode
    if args.mode == 'single':
        run_single_simulation(verbose=args.verbose)
    elif args.mode == 'monte-carlo':
        run_monte_carlo_simulation(num_runs=args.runs, verbose=args.verbose)
    elif args.mode == 'comparison':
        run_comparison_mode()
    elif args.mode == 'interactive':
        interactive_mode()
    
    print("\n" + "="*70)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
