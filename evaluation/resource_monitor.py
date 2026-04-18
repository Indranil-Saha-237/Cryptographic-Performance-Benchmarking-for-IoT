import psutil
import os
import time
import numpy as np

class ResourceMonitor:
    """Monitor CPU cycles, memory, and power consumption"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_cpu_time = None
        self.start_memory = None
        self.cpu_percent_samples = []
        
    def start_monitoring(self):
        """Start resource monitoring"""
        self.start_cpu_time = time.perf_counter()
        self.start_memory = self.process.memory_info().rss / 1024  # KB
        self.cpu_percent_samples = []
        
    def stop_monitoring(self):
        """Stop monitoring and return metrics"""
        end_cpu_time = time.perf_counter()
        end_memory = self.process.memory_info().rss / 1024  # KB
        
        # Calculate execution time
        execution_time = end_cpu_time - self.start_cpu_time
        
        # Estimate CPU cycles (approximation based on CPU frequency)
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_freq_hz = cpu_freq.current * 1e6  # Convert MHz to Hz
            else:
                cpu_freq_hz = 2.5e9  # Default 2.5 GHz if unavailable
        except:
            cpu_freq_hz = 2.5e9
        
        estimated_cycles = int(execution_time * cpu_freq_hz)
        
        # Memory delta
        memory_delta = max(0, end_memory - self.start_memory)
        
        # Power estimation
        power_estimate = self._estimate_power(execution_time)
        
        return {
            'cpu_cycles': estimated_cycles,
            'memory_usage_kb': memory_delta,
            'execution_time_sec': execution_time,
            'power_consumption_mw': power_estimate
        }
    
    def _estimate_power(self, execution_time):
        """Estimate power consumption (platform-dependent approximation)"""
        try:
            cpu_percent = self.process.cpu_percent(interval=0.01)
            # Typical laptop CPU: 15-45W under load
            # Assume linear scaling: 15W base + 30W at 100%
            estimated_power_w = 15 + (cpu_percent / 100) * 30
            return estimated_power_w * 1000  # Convert to mW
        except:
            return 25000  # Default 25W if measurement fails
