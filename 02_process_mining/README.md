# Homework 2 — Process Mining Analysis

This folder contains the submission for the process mining analysis assignment.

## Goal

Investigate whether there is a difference in throughput between domestic and international travel declarations at TU/e, and identify where in the approval process the differences arise.

## Dataset

**BPI Challenge 2020** — travel expense reimbursement process at Eindhoven University of Technology.

Two event logs are used:
- `data/DomesticDeclarations.xes` — 10,500 cases, 56,437 events
- `data/InternationalDeclarations.xes` — 6,449 cases, 72,151 events

Source: https://data.4tu.nl/collections/BPI_Challenge_2020/5065541/1

## Contents

- `REPORT.tex`: LaTeX source for the submission report.
- `REPORT.pdf`: Compiled submission report.
- `src/process_mining_hw/main.py`: Analysis script (uploaded separately as deliverable).
- `data/`: Event log datasets.
- `output/`: Generated visualizations.

## Build the Report

```bash
cd 02_process_mining/
pdflatex -interaction=nonstopmode -halt-on-error REPORT.tex
```
