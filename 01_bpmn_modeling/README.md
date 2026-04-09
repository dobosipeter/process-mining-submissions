# Homework 1 — BPMN Process Modeling

This folder contains the submission for the BPMN modeling assignment.

## Contents

- `wine_order_and_fulfillment_process.md`: Textual description of the wine order and fulfillment process.
- `REPORT.tex`: LaTeX source for the submission report.
- `REPORT.pdf`: Compiled submission report (deliverable 1).
- `wine_order_fulfillment.bpmn`: Editable BPMN diagram (deliverable 2).

## Topic

The modeled process is the **wine order and fulfillment workflow** at a family-owned winery — from receiving a customer order through to delivery and payment collection.

## Build the Report

```bash
cd 01_bpmn_modeling/
pdflatex -interaction=nonstopmode -halt-on-error REPORT.tex
```
