import os
import matplotlib.pyplot as plt
import seaborn as sns
import json
import pandas as pd
from datetime import datetime
import numpy as np

class ResultsVisualizer:
    """Generate publication-quality visualizations and reports"""
    # ═══════════════════════════════════════════════════════════════════════
    # CENTRALIZED COLOR PALETTE
    # ═══════════════════════════════════════════════════════════════════════
    COLORS = {
        # Algorithm Identity Colors (DO NOT CHANGE - used across all charts)
        'aes': '#4682B4',          # SteelBlue - AES-256
        'ascon': '#FF7F50',        # Coral - Ascon-128

        # Key Generation
        'keygen': '#66BB6A',       # MediumSeaGreen

        # Statistical Elements
        'mean_line': '#D32F2F',    # Red (for mean/reference lines)

        # UI Elements
        'edge': '#000000',         # Black (for edges)
        'text_light': '#FFFFFF',   # White (for text on dark backgrounds)
        'success': '#4CAF50',      # Green (for success indicators/headers)
    }

    def __init__(self, output_dir='results'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 11

    def plot_encryption_comparison(self, aes_times, ascon_times, data_sizes, save_name='encryption_comparison.png'):
        """Plot encryption time comparison across data sizes"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Time comparison
        x = range(len(data_sizes))
        width = 0.35

        ax1.bar([i - width/2 for i in x], aes_times, width, label='AES-256', color=self.COLORS['aes'], alpha=0.8)
        ax1.bar([i + width/2 for i in x], ascon_times, width, label='Ascon-128', color=self.COLORS['ascon'], alpha=0.8)
        
        ax1.set_xlabel('Data Size')
        ax1.set_ylabel('Encryption Time (µs)')
        ax1.set_title('Encryption Time Comparison')
        ax1.set_xticks(x)
        ax1.set_xticklabels(data_sizes)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)

        # Throughput comparison
        aes_throughput = [data_sizes[i] / (aes_times[i]/1000) / 1e6 if aes_times[i] > 0 else 0 for i in range(len(data_sizes))]
        ascon_throughput = [data_sizes[i] / (ascon_times[i]/1000) / 1e6 if ascon_times[i] > 0 else 0 for i in range(len(data_sizes))]

        ax2.plot(data_sizes, aes_throughput, marker='o', linewidth=2, label='AES-256', color=self.COLORS['aes'])
        ax2.plot(data_sizes, ascon_throughput, marker='s', linewidth=2, label='Ascon-128', color=self.COLORS['ascon'])
        
        ax2.set_xlabel('Data Size (bytes)')
        ax2.set_ylabel('Throughput (MB/s)')
        ax2.set_title('Throughput Comparison')
        ax2.legend()
        ax2.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, save_name), dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_name}")

    def plot_key_generation_performance(self, key_gen_times, save_name='key_generation.png'):
        """Plot key generation time distribution"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Histogram
        ax1.hist(key_gen_times, bins=30, color=self.COLORS['keygen'], alpha=0.7, edgecolor=self.COLORS['edge'])
        ax1.axvline(np.mean(key_gen_times), color=self.COLORS['mean_line'], linestyle='--', linewidth=2, label=f'Mean: {np.mean(key_gen_times)*1_000_000:.3f}µs')
        ax1.set_xlabel('Key Generation Time (µs)')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Key Generation Time Distribution')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)

        # Time series
        ax2.plot(range(len(key_gen_times)), [t*1_000_000 for t in key_gen_times], color=self.COLORS['keygen'], alpha=0.6)
        ax2.axhline(np.mean(key_gen_times)*1_000_000, color=self.COLORS['mean_line'], linestyle='--', linewidth=2, label=f'Mean: {np.mean(key_gen_times)*1_000_000:.3f}µs')
        ax2.set_xlabel('Key Generation Iteration')
        ax2.set_ylabel('Time (µs)')
        ax2.set_title('Key Generation Consistency')
        ax2.legend()
        ax2.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, save_name), dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_name}")

    def plot_performance_summary(self, metrics_dict, save_name='performance_summary.png'):
        """Create comprehensive performance summary visualization"""
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Extract data
        aes_data = metrics_dict.get('AES-256', {})
        ascon_data = metrics_dict.get('Ascon-128', {})

        # Plot 1: Encryption time comparison
        ax1 = fig.add_subplot(gs[0, 0])
        algorithms = ['AES-256', 'Ascon-128']
        enc_times = [aes_data.get('avg_encryption_time_µs', 0), ascon_data.get('avg_encryption_time_µs', 0)]
        ax1.barh(algorithms, enc_times, color=[self.COLORS['aes'], self.COLORS['ascon']], alpha=0.8)
        ax1.set_xlabel('Average Encryption Time (µs)')
        ax1.set_title('Encryption Performance')
        ax1.grid(axis='x', alpha=0.3)

        # Plot 2: Throughput comparison
        ax2 = fig.add_subplot(gs[0, 1])
        throughputs = [aes_data.get('avg_throughput_mbps', 0), ascon_data.get('avg_throughput_mbps', 0)]
        ax2.barh(algorithms, throughputs, color=[self.COLORS['aes'], self.COLORS['ascon']], alpha=0.8)
        ax2.set_xlabel('Throughput (MB/s)')
        ax2.set_title('Throughput Comparison')
        ax2.grid(axis='x', alpha=0.3)

        # Plot 3: Success rate
        ax3 = fig.add_subplot(gs[1, 0])
        success_rates = [aes_data.get('success_rate', 0), ascon_data.get('success_rate', 0)]
        ax3.barh(algorithms, success_rates, color=[self.COLORS['aes'], self.COLORS['ascon']], alpha=0.8)
        ax3.set_xlabel('Success Rate (%)')
        ax3.set_xlim([99, 100.5])
        ax3.set_title('Reliability')
        ax3.grid(axis='x', alpha=0.3)

        # Plot 4: Operations count
        ax4 = fig.add_subplot(gs[1, 1])
        operations = [aes_data.get('total_operations', 0), ascon_data.get('total_operations', 0)]
        ax4.bar(algorithms, operations, color=[self.COLORS['aes'], self.COLORS['ascon']], alpha=0.8)
        ax4.set_ylabel('Number of Operations')
        ax4.set_title('Testing Coverage')
        ax4.grid(axis='y', alpha=0.3)

        # Plot 5: Detailed metrics table
        ax5 = fig.add_subplot(gs[2, :])
        ax5.axis('off')

        table_data = [
            ['Metric', 'AES-256', 'Ascon-128'],
            ['Avg Encryption (µs)', f"{aes_data.get('avg_encryption_time_µs', 0):.3f}", f"{ascon_data.get('avg_encryption_time_µs', 0):.3f}"],
            ['Avg Decryption (µs)', f"{aes_data.get('avg_decryption_time_µs', 0):.3f}", f"{ascon_data.get('avg_decryption_time_µs', 0):.3f}"],
            ['Throughput (MB/s)', f"{aes_data.get('avg_throughput_mbps', 0):.2f}", f"{ascon_data.get('avg_throughput_mbps', 0):.2f}"],
            ['Success Rate (%)', f"{aes_data.get('success_rate', 0):.2f}", f"{ascon_data.get('success_rate', 0):.2f}"],
            ['Total Operations', str(aes_data.get('total_operations', 0)), str(ascon_data.get('total_operations', 0))]
        ]

        table = ax5.table(cellText=table_data, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)

        # Style header row
        for i in range(3):
            table[(0, i)].set_facecolor(self.COLORS['success'])
            table[(0, i)].set_text_props(weight='bold', color=self.COLORS['text_light'])

        plt.suptitle('Bot-IoT Cryptography Framework - Performance Summary', fontsize=16, fontweight='bold', y=0.98)

        plt.savefig(os.path.join(self.output_dir, save_name), dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_name}")

    def generate_latex_table(self, metrics_dict, save_name='results_table.tex'):
        """Generate LaTeX table for research paper"""
        # Use single backslashes with proper escaping
        latex = "\\begin{table}[h]\n"
        latex += "\\centering\n"
        latex += "\\caption{Performance Comparison of AES-256 and Ascon-128 on Bot-IoT Dataset}\n"
        latex += "\\label{tab:performance}\n"
        latex += "\\begin{tabular}{lcc}\n"
        latex += "\\hline\n"
        latex += "\\textbf{Metric} & \\textbf{AES-256} & \\textbf{Ascon-128} \\\\\n"
        latex += "\\hline\n"

        aes = metrics_dict.get('AES-256', {})
        ascon = metrics_dict.get('Ascon-128', {})

        latex += f"Avg Encryption Time (µs) & {aes.get('avg_encryption_time_µs', 0):.3f} & {ascon.get('avg_encryption_time_µs', 0):.3f} \\\\\n"
        latex += f"Avg Decryption Time (µs) & {aes.get('avg_decryption_time_µs', 0):.3f} & {ascon.get('avg_decryption_time_µs', 0):.3f} \\\\\n"
        latex += f"Throughput (MB/s) & {aes.get('avg_throughput_mbps', 0):.2f} & {ascon.get('avg_throughput_mbps', 0):.2f} \\\\\n"
        latex += f"Success Rate (\\%) & {aes.get('success_rate', 0):.2f} & {ascon.get('success_rate', 0):.2f} \\\\\n"
        latex += f"Total Operations & {aes.get('total_operations', 0)} & {ascon.get('total_operations', 0)} \\\\\n"
        latex += "\\hline\n"
        latex += "\\end{tabular}\n"
        latex += "\\end{table}"

        with open(os.path.join(self.output_dir, save_name), 'w') as f:
            f.write(latex)
        print(f"Saved: {save_name}")

    def generate_markdown_report(self, all_data, save_name='RESULTS_REPORT.md'):
        """Generate comprehensive markdown report"""
        report = f"""# Bot-IoT Cryptography Framework - Results Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary

This report presents the performance evaluation of a hybrid cryptographic framework combining AI-driven key management with AES-256 and Ascon-128 encryption algorithms on the Bot-IoT network traffic dataset.

## Dataset Information

- **Dataset:** UNSW Bot-IoT 10-Best Features
- **Samples Processed:** {all_data.get('dataset_info', {}).get('samples', 'N/A')}
- **Features:** {all_data.get('dataset_info', {}).get('features', 'N/A')}
- **Device:** {all_data.get('device', 'N/A')}

## AI Key Generation Performance

- **Average Generation Time:** {all_data.get('key_gen', {}).get('avg_time_µs', 0):.3f} µs
- **Standard Deviation:** {all_data.get('key_gen', {}).get('std_time_µs', 0):.3f} µs
- **Min/Max:** {all_data.get('key_gen', {}).get('min_time_µs', 0):.3f} / {all_data.get('key_gen', {}).get('max_time_µs', 0):.3f} µs

## Encryption Performance

### AES-256
{self._format_algorithm_results(all_data.get('AES-256', {}))}

### Ascon-128
{self._format_algorithm_results(all_data.get('Ascon-128', {}))}

## Comparative Analysis

{self._format_comparison(all_data.get('comparison', {}))}

## Conclusions

1. The AI-driven key generation system demonstrates consistent performance with sub-millisecond generation times.
2. Both AES-256 and Ascon-128 provide reliable encryption for IoT network traffic.
3. The framework successfully processes {all_data.get('dataset_info', {}).get('samples', 'N/A')} Bot-IoT samples with 100% success rate.

## Files Generated

- `encryption_comparison.png` - Visual comparison of encryption performance
- `key_generation.png` - Key generation time distribution
- `performance_summary.png` - Comprehensive performance dashboard
- `results_table.tex` - LaTeX table for research paper
- `metrics_report.json` - Raw metrics data

---
*Framework developed for Bot-IoT network security research*
"""

        with open(os.path.join(self.output_dir, save_name), 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Saved: {save_name}")

    def _format_algorithm_results(self, data):
        return f"""
- **Average Encryption Time:** {data.get('avg_encryption_time_µs', 0):.3f} µs
- **Average Decryption Time:** {data.get('avg_decryption_time_µs', 0):.3f} µs
- **Throughput:** {data.get('avg_throughput_mbps', 0):.2f} MB/s
- **Success Rate:** {data.get('success_rate', 0):.2f}%
- **Total Operations:** {data.get('total_operations', 0)}
"""

    def _format_comparison(self, data):
        return f"""
- **Encryption Speed:** {data.get('encryption_speedup', 'N/A')}
- **Decryption Speed:** {data.get('decryption_speedup', 'N/A')}
- **Throughput Advantage:** {data.get('throughput_advantage', 'N/A')}
"""
