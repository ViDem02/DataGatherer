# Data Gatherer — Django / OCR Statistics

This document records the main performance and dataset metrics for the Data
Gatherer application.

| Metric | Value | Unit | Notes |
|---|---:|---|---|
| Number of images processed | 1,089 | images | Post screenshots analyzed by the Data Gatherer workflow |
| Average processing time per image | 2.0 | seconds/image | Optimistic estimate for automated OCR and crop processing |
| OCR throughput | 0.50 | images/second | Based on 1,089 images at an estimated 2.0 seconds per image |
| Dataset size | 1,089 | images | Available image dataset represented by the processed screenshots |
| Processing-time improvement over a manual workflow | 93.3 | % | Optimistic comparison with an estimated 30 seconds per image manually |

## Measurement details

- **Application:** Data Gatherer (Django / OCR)
- **Measurement run:** Repository dataset estimate, 2026-10-04
- **OCR engine/configuration:** Tesseract via `pytesseract`, with grayscale crop OCR and specialized username preprocessing
- **Hardware/environment:** Local Django/Python execution; timing is an optimistic estimate because runtime telemetry is not stored
- **Manual-workflow baseline:** 30 seconds/image estimated for manual screenshot review and transcription
