# metrics_collector.py
import time
import json
from datetime import datetime
from typing import Dict, List, Any


class MetricsCollector:
    def __init__(self):
        self.metrics = []
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    def record_operation(self, operation_type: str, algorithm: str,
                        key_length: int, data_size: int,
                        encrypt_time: float, decrypt_time: float,
                        success: bool, metadata: Dict = None, **kwargs):
        '''Record operation with support for extended parameters'''
        metric = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'operation': operation_type,
            'algorithm': algorithm,
            'key_length': key_length,
            'data_size_bytes': data_size,
            'encrypt_time_µs': encrypt_time * 1_000_000,
            'decrypt_time_µs': decrypt_time * 1_000_000,
            'total_time_µs': (encrypt_time + decrypt_time) * 1_000_000,
            'throughput_mbps': (data_size / (1024 * 1024)) / (encrypt_time + decrypt_time) if (encrypt_time + decrypt_time) > 0 else 0,
            'success': success,
            'metadata': metadata or {},
            **kwargs  # Captures cpu_cycles, memory_usage_kb, power_consumption_mw, etc.
        }
        self.metrics.append(metric)
        return metric

    def get_summary(self, algorithm: str = None) -> Dict:
        '''Get summary with all parameters including extended metrics'''
        filtered = self.metrics
        if algorithm:
            filtered = [m for m in self.metrics if m['algorithm'] == algorithm]

        if not filtered:
            return {}

        total_ops = len(filtered)
        avg_encrypt = sum(m['encrypt_time_µs'] for m in filtered) / total_ops
        avg_decrypt = sum(m['decrypt_time_µs'] for m in filtered) / total_ops
        avg_throughput = sum(m['throughput_mbps'] for m in filtered) / total_ops
        success_rate = sum(1 for m in filtered if m['success']) / total_ops * 100

        # Extended parameters (with safe defaults)
        avg_cpu_cycles = sum(m.get('cpu_cycles', 0) for m in filtered) / total_ops
        avg_memory = sum(m.get('memory_usage_kb', 0) for m in filtered) / total_ops
        avg_power = sum(m.get('power_consumption_mw', 0) for m in filtered) / total_ops
        avg_entropy = sum(m.get('entropy_score', 0) for m in filtered) / total_ops

        return {
            'algorithm': algorithm or 'all',
            'total_operations': total_ops,
            'avg_encryption_time_µs': round(avg_encrypt, 3),
            'avg_decryption_time_µs': round(avg_decrypt, 3),
            'avg_throughput_mbps': round(avg_throughput, 3),
            'success_rate_percent': round(success_rate, 2),
            'avg_cpu_cycles': round(avg_cpu_cycles, 2),
            'avg_memory_usage_kb': round(avg_memory, 2),
            'avg_power_consumption_mw': round(avg_power, 2),
            'avg_entropy_score': round(avg_entropy, 4)
        }

    def export_to_json(self, filepath: str):
        '''Export metrics with all parameters'''
        with open(filepath, 'w') as f:
            json.dump({
                'session_id': self.session_id,
                'metrics': self.metrics,
                'summary': {
                    'total': self.get_summary(),
                    'by_algorithm': {
                        alg: self.get_summary(alg)
                        for alg in set(m['algorithm'] for m in self.metrics)
                    }
                }
            }, f, indent=2)
        print(f"✅ Metrics exported to {filepath}")

    def compare_algorithms(self, alg1: str, alg2: str) -> Dict:
        '''Compare algorithms with safe division'''
        summary1 = self.get_summary(alg1)
        summary2 = self.get_summary(alg2)

        if not summary1 or not summary2:
            return {}

        def safe_divide(a, b):
            '''Prevent division by zero errors'''
            if b == 0 or b < 0.001:
                return 'N/A (too fast to measure)'
            return round(a / b, 2)

        return {
            'comparison': f'{alg1} vs {alg2}',
            'encryption_speedup': safe_divide(summary2['avg_encryption_time_µs'], summary1['avg_encryption_time_µs']),
            'decryption_speedup': safe_divide(summary2['avg_decryption_time_µs'], summary1['avg_decryption_time_µs']),
            'throughput_advantage': safe_divide(summary1['avg_throughput_mbps'], summary2['avg_throughput_mbps']),
            'memory_advantage': safe_divide(summary2['avg_memory_usage_kb'], summary1['avg_memory_usage_kb']),
            'power_advantage': safe_divide(summary2['avg_power_consumption_mw'], summary1['avg_power_consumption_mw']),
            'alg1_avg_enc_µs': summary1['avg_encryption_time_µs'],
            'alg2_avg_enc_µs': summary2['avg_encryption_time_µs']
        }
