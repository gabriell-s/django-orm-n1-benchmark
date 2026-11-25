#!/usr/bin/env python3
import csv
import os
from collections import defaultdict
from pathlib import Path

def read_benchmark_csv_files(directory):
    """Read all CSV files from the benchmark directory and aggregate data."""
    # Structure: {endpoint: {metric: {page_size: {strategy: [values]}}}}
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    
    csv_files = sorted(Path(directory).glob("api_benchmark_*.csv"))
    
    for csv_file in csv_files:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                endpoint = row['endpoint']
                strategy = row['strategy']
                page_size = int(row['page_size'])
                time_ms = float(row['time_ms'])
                query_count = int(row['query_count'])
                
                # Store data for each endpoint, metric, page size, and strategy
                data[endpoint]['time'][page_size][strategy].append(time_ms)
                data[endpoint]['query'][page_size][strategy].append(query_count)
    
    return data

def calculate_averages(data):
    """Calculate averages for each strategy and page size."""
    averages = {}
    for endpoint, metrics in data.items():
        averages[endpoint] = {}
        for metric, page_sizes in metrics.items():
            averages[endpoint][metric] = {}
            for page_size, strategies in page_sizes.items():
                averages[endpoint][metric][page_size] = {}
                for strategy, values in strategies.items():
                    averages[endpoint][metric][page_size][strategy] = sum(values) / len(values)
    
    return averages

def format_table(averages_per_endpoint, metric, metric_label):
    """Format a single table for a metric."""
    page_sizes = sorted(averages_per_endpoint[metric].keys())
    
    # Define strategy mappings
    strategy_map = {
        'none': 'Normal',
        'select=true': 'Com Select',
        'prefetch=true': 'Com Prefetch',
        'prefetch=true&select=true': 'Com ambos',
        'prefetch_select=true': 'Com Prefetch*'
    }
    
    # Build the output
    lines = []
    
    # Title line
    lines.append(f'{metric_label}:')
    
    # Header row with page sizes
    header = '\t' + '\t'.join(str(size) for size in page_sizes)
    lines.append(header)
    
    # Data rows for each strategy
    for display_name in ['Normal', 'Com Select', 'Com Prefetch', 'Com ambos', 'Com Prefetch*']:
        # Find the strategy key that maps to this display name
        strategy_key = [k for k, v in strategy_map.items() if v == display_name][0]
        
        row_values = [display_name]
        for page_size in page_sizes:
            if strategy_key in averages_per_endpoint[metric].get(page_size, {}):
                value = averages_per_endpoint[metric][page_size][strategy_key]
                row_values.append(f'{value:.2f}')
            else:
                row_values.append('N/A')
        
        lines.append('\t'.join(row_values))
    
    return '\n'.join(lines)

def main():
    benchmark_dir = Path(__file__).parent / 'resultados_tcc'
    
    if not benchmark_dir.exists():
        print(f"Error: Directory {benchmark_dir} not found")
        return
    
    print(f"Reading CSV files from {benchmark_dir}...")
    data = read_benchmark_csv_files(benchmark_dir)
    
    print("Calculating averages...")
    averages = calculate_averages(data)
    
    # Write output files per endpoint
    output_dir = Path(__file__).parent
    
    for endpoint, metrics_data in averages.items():
        endpoint_name = endpoint.strip('/').replace('/', '_')
        
        # Create combined output
        output_lines = []
        output_lines.append(f"=== {endpoint} ===\n")
        
        # Time table
        time_table = format_table(metrics_data, 'time', 'Time (ms)')
        output_lines.append(time_table)
        
        # Separator
        output_lines.append('\n' + '-' * 80 + '\n')
        
        # Query table
        query_table = format_table(metrics_data, 'query', 'Query Count')
        output_lines.append(query_table)
        
        output_text = '\n'.join(output_lines)
        
        # Write to single file per endpoint
        output_file = output_dir / f'benchmark_{endpoint_name}.txt'
        with open(output_file, 'w') as f:
            f.write(output_text)
        
        print(f"\nSummary saved to: {output_file}")
        print(output_text)
        print("\n")

if __name__ == '__main__':
    main()
