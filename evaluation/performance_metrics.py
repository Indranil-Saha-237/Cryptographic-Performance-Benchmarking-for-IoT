import json
import time
import numpy as np
import os
from datetime import datetime
from collections import defaultdict

class PerformanceMetrics:
    def __init__(self, project_root):
        self.project_root = project_root
        self.metrics_data = {
            'timestamp': datetime.now().isoformat(),
            'key_generation': defaultdict(list),
            'encryption': defaultdict(list),
            'decryption': defaultdict(list),
            'key_rotation': defaultdict(list),
            'summary': {}
        }
        self.start_times = {}

    def start_operation(self, operation_id):
        """Start timing an operation"""
        self.start_times[operation_id] = time.time()

    def end_operation(self, operation_id, operation_type, method_name, data_size=None):
        """End timing and record operation"""
        if operation_id not in self.start_times:
            raise ValueError(f"Operation {operation_id} not started")

        elapsed_ms = (time.time() - self.start_times[operation_id]) * 1000
        del self.start_times[operation_id]

        record = {
            'method': method_name,
            'time_ms': elapsed_ms,
            'timestamp': datetime.now().isoformat()
        }

        if data_size:
            record['data_size_bytes'] = data_size

            # FIX: Only calculate throughput if elapsed_ms is meaningful (> 0.001ms)
            if elapsed_ms > 0.001:
                record['throughput_mbps'] = (data_size / 1024 / 1024) / (elapsed_ms / 1000)
            else:
                # For extremely fast operations, mark as infinite throughput
                record['throughput_mbps'] = float('inf')

        self.metrics_data[operation_type][method_name].append(record)
        return elapsed_ms

    def calculate_statistics(self):
        """Calculate aggregated statistics"""
        stats = {}

        for operation_type in ['key_generation', 'encryption', 'decryption', 'key_rotation']:
            stats[operation_type] = {}

            for method_name, records in self.metrics_data[operation_type].items():
                if not records:
                    continue

                times = [r['time_ms'] for r in records]

                stats[operation_type][method_name] = {
                    'count': len(records),
                    'avg_time_ms': np.mean(times),
                    'std_time_ms': np.std(times),
                    'min_time_ms': np.min(times),
                    'max_time_ms': np.max(times),
                    'median_time_ms': np.median(times),
                    'p95_time_ms': np.percentile(times, 95),
                    'p99_time_ms': np.percentile(times, 99)
                }

                # FIX: Handle infinite throughputs in statistics
                throughputs = [r.get('throughput_mbps', 0) for r in records 
                             if 'throughput_mbps' in r and r['throughput_mbps'] != float('inf')]
                if throughputs:
                    stats[operation_type][method_name]['avg_throughput_mbps'] = np.mean(throughputs)
                elif any('throughput_mbps' in r for r in records):
                    stats[operation_type][method_name]['avg_throughput_mbps'] = float('inf')

        self.metrics_data['summary'] = stats
        return stats

    def export_to_json(self, filename='performance_metrics.json'):
        """Export metrics to JSON file"""
        export_data = {
            'timestamp': self.metrics_data['timestamp'],
            'summary': {},
            'detailed_metrics': {}
        }

        for op_type, methods in self.metrics_data['summary'].items():
            export_data['summary'][op_type] = {}
            for method, stats in methods.items():
                export_data['summary'][op_type][method] = {}
                for k, v in stats.items():
                    if v == float('inf'):
                        export_data['summary'][op_type][method][k] = "INFINITY"
                    else:
                        export_data['summary'][op_type][method][k] = float(v) if isinstance(v, (int, float, np.number)) else v

        filepath = os.path.join(self.project_root, 'evaluation', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

        return filepath

    def generate_report(self):
        """Generate a human-readable performance report"""
        report = []
        report.append("=" * 80)
        report.append("PERFORMANCE METRICS REPORT")
        report.append(f"Generated: {self.metrics_data['timestamp']}")
        report.append("=" * 80)

        stats = self.metrics_data['summary']

        for op_type in ['key_generation', 'encryption', 'decryption', 'key_rotation']:
            if op_type not in stats or not stats[op_type]:
                continue

            report.append(f"\n{op_type.upper().replace('_', ' ')}")
            report.append("-" * 80)

            for method, method_stats in stats[op_type].items():
                report.append(f"\n  Method: {method}")
                report.append(f"  Count: {method_stats['count']}")
                report.append(f"  Average: {method_stats['avg_time_ms']:.3f}ms")
                report.append(f"  Std Dev: {method_stats['std_time_ms']:.3f}ms")
                report.append(f"  Min/Max: {method_stats['min_time_ms']:.3f}ms / {method_stats['max_time_ms']:.3f}ms")
                report.append(f"  Median: {method_stats['median_time_ms']:.3f}ms")
                report.append(f"  P95/P99: {method_stats['p95_time_ms']:.3f}ms / {method_stats['p99_time_ms']:.3f}ms")

                if 'avg_throughput_mbps' in method_stats:
                    throughput = method_stats['avg_throughput_mbps']
                    if throughput == float('inf'):
                        report.append(f"  Throughput: VERY FAST (< 1ms)")
                    else:
                        report.append(f"  Throughput: {throughput:.2f} Mbps")

        report.append("\n" + "=" * 80)
        return "\n".join(report)
