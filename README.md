# Anomaly Detection in Public Dataset Query Logs

> *Can one model rule them all, or does each anomaly type need its own bouncer?*

This repository contains all code, experiments, and visuals from the research paper **"Detecting Anomalies in Public Datasets Using Query Logs"**. The paper builds a unified detection framework using unsupervised hybrid ML models and evaluates whether a single model can handle all anomaly types — or whether each needs a dedicated detector.

---

## The Core Question

Query logs are a goldmine of behavioral signals. A well-behaved query looks like a regular customer. An anomalous one looks like someone who walked into a bank, asked for the vault password, and came back at 3am with a drill.

This paper formalizes three classes of such "customers":

### Anomaly Categories

| Category | What It Looks Like |
|---|---|
| **Security** | Unusual query structure, access to sensitive tables outside normal patterns, SQL injection-like signatures |
| **Temporal** | Queries firing at wrong times, frequency spikes, bulk ops outside operational windows |
| **Performance** | Execution time deviating significantly from historical baseline for that query type |

---

## Models Used

All models are **unsupervised** — no labeled anomalies needed at training time.

- **Isolation Forest** — Isolates anomalies by randomly partitioning feature space. Think of it as: weird points need fewer cuts to isolate. Fast, works well on high-dimensional data.
- **DBSCAN** — Density-based clustering. Points in sparse regions = anomalies. Great for temporal clustering and frequency spikes.
- **One-Class SVM** — Learns a tight boundary around "normal". Anything outside is flagged. Works well for performance deviation where normal has a clear distribution.

The hybrid framework combines outputs from all three to produce a unified anomaly score.

---

## Datasets

| Role | Dataset | Description |
|---|---|---|
| **Benchmark** | [TPC-H v3.0.1](https://www.tpc.org/TPC_Documents_Current_Versions/pdf/TPC-H_v3.0.1.pdf) | Industry-standard decision support benchmark; used to define "normal" query workloads |
| **Actual** | [Pagila](https://github.com/devrimgunduz/pagila) | PostgreSQL port of Sakila (DVD rental DB); used as the real-world target dataset |

Synthetic anomalies were injected into Pagila query logs across all three categories for evaluation.

---

## Key Results (Summary)

The paper answers the main question empirically. Spoiler: it's not a clean "one model wins" story.

- **Isolation Forest** generalizes reasonably across all three categories but misses subtle temporal patterns.
- **DBSCAN** dominates temporal anomaly detection; struggles with performance deviations.
- **One-Class SVM** is the sharpest tool for performance anomalies but expensive to tune.
- The **hybrid framework** outperforms any single model across all categories — specialization matters, but ensemble coordination wins.

Full results, confusion matrices, and F1/Precision/Recall breakdowns are in `evaluation/` and the paper.

---
