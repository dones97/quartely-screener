# Quarterly Data Stock Screener

This repository implements a fundamental stock screener for Indian equities, using **quarterly financial data** to provide richer, more granular screening than typical annual-based screeners.

---

## Purpose

- **More Data Points:** Overcomes the limitations of annual data (usually only 4–5 years available) by using every available quarter, increasing datapoints for screening and trend analysis.
- **Flexible Screening:** Screen by quarterly YoY growth, sequential growth, and net profit margin (NPM), with percentile/industry comparisons.
- **Independent:** This repository is **separate** from any annual data screener you may use.

---

## Repository Structure

```
quarterly-screener/
│
├── data/                # Source and processed quarterly data (CSV, parquet, etc.)
│   ├── raw/             # Raw downloaded quarterly financial
