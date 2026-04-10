# Homework 2 — Process Mining Analysis

This folder contains the submission for the process mining analysis assignment.

## Goal

Investigate whether there is a difference in throughput between domestic and international travel declarations at TU/e, and identify where in the approval process the differences arise.

## Dataset

**BPI Challenge 2020** — travel expense reimbursement process at Eindhoven University of Technology.

Two event logs are used:
- `data/DomesticDeclarations.xes.gz` — 10,500 cases, 56,437 events
- `data/InternationalDeclarations.xes.gz` — 6,449 cases, 72,151 events

Source: https://data.4tu.nl/collections/BPI_Challenge_2020/5065541/1

## Contents

- `REPORT.tex` / `REPORT.pdf`: Submission report (LaTeX source + compiled PDF).
- `src/process_mining_hw/main.py`: Analysis script (uploaded separately as deliverable).
- `data/`: Event log datasets (compressed XES).
- `output/`: Generated visualizations (26 PNG files).
- `models/`: Exported process models (6 PNML Petri nets + 2 BPMN models).

## Reproducing the Analysis

### Prerequisites

- Python >= 3.10
- [Graphviz](https://graphviz.org/download/) (required by pm4py for model visualization)
- pdflatex (for compiling the report)

### Setup

```bash
cd 02_process_mining/
python -m venv .venv
source .venv/bin/activate
pip install pm4py pandas numpy matplotlib
```

### Run the analysis

```bash
python -m process_mining_hw.main
```

This loads both event logs, runs the full analysis pipeline (exploratory statistics, throughput comparison, duration decomposition, process discovery with three algorithms, conformance checking), and saves all outputs to `output/` and `models/`. Existing output files are skipped automatically.

### Build the report

```bash
pdflatex -interaction=nonstopmode -halt-on-error REPORT.tex
pdflatex -interaction=nonstopmode -halt-on-error REPORT.tex  # second pass for cross-references
```
