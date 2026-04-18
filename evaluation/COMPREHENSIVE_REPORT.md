# Comprehensive Cryptographic Performance Analysis

## Executive Summary

This report presents a comprehensive evaluation of AES-256 and ASCON-128 cryptographic algorithms across **7 parameter categories**.

**Test Environment:**
- Session ID: 20251228_220105
- Total Operations: 8

## Performance Comparison Table

| Data Size   | Algorithm   |   Enc Time (탎) |   Dec Time (탎) |   Throughput (MB/s) | CPU Cycles   |   Cycles/Byte |   Memory (KB) |   Power (mW) |   Entropy |   Overhead (%) |
|:------------|:------------|----------------:|----------------:|--------------------:|:-------------|--------------:|--------------:|-------------:|----------:|---------------:|
| 140B        | AES-256     |           111.6 |           136.1 |                0.54 | 342,300      |       2445    |             0 |        15000 |    6.7436 |          11.43 |
| 140B        | ASCON-128   |          1519.6 |          1234.4 |                0.05 | 3,293,639    |      23526    |             0 |        15000 |    6.8302 |          31.43 |
| 1.4KB       | AES-256     |           189.3 |            87   |                5.8  | 494,129      |        294.12 |             0 |        15000 |    7.8885 |           0.95 |
| 1.4KB       | ASCON-128   |          8753.8 |         10335.2 |                0.08 | 18,468,659   |      10993.2  |             4 |        15000 |    7.8693 |           2.62 |
| 14KB        | AES-256     |           206.5 |           212.2 |               31.89 | 491,820      |         35.13 |             0 |        46260 |    7.9862 |           0.11 |
| 14KB        | ASCON-128   |         60474.3 |         58245.5 |                0.11 | 87,903,448   |       6278.82 |            28 |        15000 |    7.9869 |           0.31 |
| 140KB       | AES-256     |           626.2 |           430.3 |               50.55 | 951,424      |         16.99 |           112 |        15000 |    7.9964 |           0.03 |
| 140KB       | ASCON-128   |        257105   |        223364   |                0.11 | 539,977,410  |       9642.45 |             4 |        15000 |    7.9969 |           0.08 |

## Summary Statistics

| Algorithm   |   Avg Enc (탎) |   Avg Dec (탎) |   Avg Throughput (MB/s) | Avg CPU Cycles   |   Avg Cycles/Byte |   Avg Memory (KB) |   Avg Power (mW) |   Avg Entropy | Success Rate   |
|:------------|---------------:|---------------:|------------------------:|:-----------------|------------------:|------------------:|-----------------:|--------------:|:---------------|
| AES-256     |          283.4 |          216.4 |                   22.19 | 569,918          |            697.81 |                28 |            22815 |        7.6537 | 100%           |
| Ascon-128   |        81963.2 |        73294.8 |                    0.09 | 162,410,789      |          12610.1  |                 9 |            15000 |        7.6708 | 100%           |

## Key Findings

### 1. Throughput & Latency
- **AES-256**: 283.4000 탎 average encryption
- **ASCON-128**: 81963.1750 탎 average encryption

### 2. CPU Efficiency
- **AES-256**: 697.81 cycles/byte
- **ASCON-128**: 12610.13 cycles/byte

### 3. Resource Usage
- **AES-256**: 22815.00 mW power
- **ASCON-128**: 15000.00 mW power

### 4. Security
- **AES-256**: Entropy 7.6537/8.0
- **ASCON-128**: Entropy 7.6708/8.0

## Conclusion

All 7 parameter categories successfully measured and documented for research publication.

---
*Generated: 2025-12-28 22:01:08.352144*
