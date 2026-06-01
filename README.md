# Anomaly Detection in Public Datasets using Query Logs

This repository contains the complete implementation, datasets, evaluation scripts, and visualizations for our research paper on detecting multi-category anomalies in database query logs using unsupervised hybrid machine learning models.

The core objective of this research is to build a unified detection framework and answer a critical architectural question: **Can a single machine learning model accurately detect security, temporal, and performance anomalies simultaneously, or does each anomaly category require a specialized detector?**

---

## 📌 Project Overview

Database query logs are rich sources of operational telemetry. This project benchmarks how effectively unsupervised machine learning can flag malicious, inefficient, or structurally anomalous database activity without labeled training data.

### Anomaly Taxonomy
The framework classifies anomalies into three distinct categories:
1. **Security Anomalies:** Unusual query structures, access to sensitive tables outside normal user patterns, and structural signatures resembling SQL injection attacks.
2. **Temporal Anomalies:** Queries executing at irregular hours, unexpected frequency spikes, and high-volume bulk operations running outside scheduled operational windows.
3. **Performance Anomalies:** Query execution times deviating significantly from the established historical baseline for that specific query type.

---

## 🛠️ Methodology & Models

We implement and evaluate a unified framework utilizing three core unsupervised hybrid machine learning architectures:
* **Isolation Forest:** For isolating global anomalies and high-dimensional outliers via random partitioning.
* **DBSCAN (Density-Based Spatial Clustering of Applications with Noise):** For identifying dense clusters of normal behavior and flagging low-density queries as noise/anomalies.
* **One-Class SVM:** For learning a non-linear decision boundary around standard operating queries to detect novel deviations.

---

## 📊 Datasets

The models are validated using two distinct query log environments:

1.  **Benchmark Dataset:** Standardized analytical query workloads generated from the [TPC-H Benchmark (v3.0.1)](https://www.tpc.org/TPC_Documents_Current_Versions/pdf/TPC-H_v3.0.1.pdf). This provides predictable baseline patterns to test the models' precision boundaries.
2.  **Actual/Production Dataset:** Relational OLTP query logs derived from the [Pagila (PostgreSQL sample database)](https://github.com/devrimgunduz/pagila/tree/master) schema, simulated with synthetic user traffic, maintenance jobs, and injected anomalies.

---

## 📂 Repository Structure

```text
├── data/                  # TPC-H and Pagila query logs (raw and preprocessed)
├── src/
│   ├── preprocessing/     # Query parsing, tokenization, and feature extraction
│   ├── models/            # Isolation Forest, DBSCAN, and One-Class SVM implementations
│   └── evaluation/        # Performance metrics, baseline comparison scripts
├── visuals/               # ROC curves, t-SNE cluster plots, and anomaly distributions
├── notebooks/             # Exploratory Data Analysis (EDA) and model prototyping
├── requirements.txt       # Python dependencies
└── README.md
