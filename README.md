# README: Performance-Based Comparison of AES-256 and ASCON-128

This repository contains the supplemental materials and documentation for the book chapter titled **"Metaverse Security: Performance Evaluation of Techniques "** approved by **IGI Global Scientific Publishing** and will be published in due time.

---

## Chapter Overview
This research explores the trade-offs between **high-throughput** and **lightweight** cryptographic design philosophies. By benchmarking **AES-256** (a high-performance block cipher) against **ASCON-128** (the NIST-standardized lightweight authenticated encryption algorithm), this chapter provides a multi-metric evaluation across diverse deployment environments, including **IoT**, **Cloud-Edge**, and the **Metaverse**.

### Key Objectives
**Analyze Performance:** Evaluate latency, throughput, CPU efficiency (cycles-per-byte), and memory footprint.
**Assess Security:** Validate statistical randomness via Shannon Entropy and test resilience against bit-flip and timing attacks.
**Contextual Selection:** Provide strategic guidance for choosing encryption standards based on workload profiles.

---

## Performance Highlights
| Metric | AES-256 Strength | ASCON-128 Strength |
| :--- | :--- | :--- |
| **Throughput** | High (scales to 44.1 MB/s) | Limited (0.05–0.09 MB/s)  |
| **Efficiency** | Best for large data streams  | Predictable for small payloads  |
| **Memory** | Larger code/runtime footprint  | Ultra-compact (approx. 9 KB avg)  |
| **AEAD** | Requires external modes (e.g., GCM)  | Built-in authentication  |

---

## Data
The performance metrics and experimental results were derived using standardized payloads (140B, 1.4KB, 14KB, and 140KB) to simulate real-world IoT and telemetry traffic .

### Accessing the Dataset
To reproduce the findings or use the benchmarking data in your own analysis, follow these steps:

1.  **Download the dataset:** Access the raw experimental results and synthetic/Bot-IoT datasets from the following link: **https://www.kaggle.com/datasets/vigneshvenkateswaran/bot-iot**.
2.  **Placement:** Extract the contents of the downloaded ZIP file.
3.  **Directory Structure:** Place the extracted files into the `/archive` folder within your local project directory.
    * Example path: `your-project-root/archive/results_table1.csv`
4.  **Verification:** Ensure that the data files align with the values reported in **Table 1** (Payload-wise metrics) and **Table 2** (Aggregate averages) of the chapter[cite: 332, 339].

---

## Application Contexts
This research highlights specific optimization strategies for different technological sectors:
**Border Security & UAVs:** AES-256 is recommended for high-resolution video and situational awareness data due to its sublinear scaling and low latency.
**IoT Sensor Networks:** ASCON-128 is the ideal choice for battery-operated devices with severe memory constraints.
**Metaverse Architecture:** A hybrid model is proposed, utilizing ASCON-128 for wearables/sensors and AES-256 for high-performance rendering servers.

---
