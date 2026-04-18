import numpy as np
from scipy import stats

class SecurityMetrics:
    """Calculate entropy and randomness metrics"""
    
    def calculate_entropy(self, data):
        """Calculate Shannon entropy (bits per byte)"""
        if isinstance(data, str):
            data = bytes.fromhex(data)
        
        # Count byte frequencies
        byte_counts = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
        probabilities = byte_counts / len(data)
        probabilities = probabilities[probabilities > 0]
        
        # Shannon entropy
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return entropy  # Max = 8.0 for perfect randomness
    
    def chi_square_uniformity(self, data):
        """Chi-square test for uniform byte distribution"""
        if isinstance(data, str):
            data = bytes.fromhex(data)
        
        observed = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
        expected = len(data) / 256
        
        chi2, p_value = stats.chisquare(observed, [expected]*256)
        
        return {
            'chi2_statistic': chi2,
            'p_value': p_value,
            'is_random': p_value > 0.01  # 99% confidence
        }
    
    def runs_test(self, data):
        """Wald-Wolfowitz runs test for randomness"""
        if isinstance(data, str):
            data = bytes.fromhex(data)
        
        bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        median = np.median(bits)
        
        # Count runs
        runs = 1
        for i in range(1, len(bits)):
            if (bits[i] > median) != (bits[i-1] > median):
                runs += 1
        
        # Expected runs and variance
        n = len(bits)
        n_above = np.sum(bits > median)
        n_below = n - n_above
        
        if n_above == 0 or n_below == 0:
            return {'runs': runs, 'z_score': 0, 'is_random': False}
        
        expected_runs = (2 * n_above * n_below / n) + 1
        variance = (2 * n_above * n_below * (2 * n_above * n_below - n)) / (n**2 * (n - 1))
        
        if variance > 0:
            z_score = (runs - expected_runs) / np.sqrt(variance)
        else:
            z_score = 0
        
        return {
            'runs': runs,
            'expected_runs': expected_runs,
            'z_score': z_score,
            'is_random': abs(z_score) < 1.96  # 95% confidence
        }
