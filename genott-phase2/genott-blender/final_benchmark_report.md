# Final Benchmark Report (100 Movies E2E Test)

## Core Metrics
| Metric | Value |
|--------|-------|
| Success Rate | 94.0% |
| Total Movies Run | 100 |
| Successful Generations | 94 |
| Quality Engine Rejections | 0 |
| Pipeline Failures | 6 |
| Average Movie Duration | 2.67s |
| Average Render Time | 18.80s |
| Average Quality Score | 72.0/100 |
| Most Common Failure | BLENDER |
| Total Benchmark Time | 1880.01s |

## Failure Category Breakdown
| Category | Failures Tracked | Description |
|----------|------------------|-------------|
| Render Failures | 2 | General exceptions, network timeouts, unhandled crashes |
| Blender Failures | 4 | Blender daemon crashes, scene building errors |
| FFmpeg Failures | 0 | Stitching / concatenation / audio merge failures |
| Audio Failures | 0 | Edge-TTS speech generation problems |
| Transition Failures | 0 | Invalid transition processing between scenes |
| Continuity Failures | 0 | Scene continuity or character matching discrepancies |

## Genre Analysis
| Genre | Runs | Success Rate | Average Score | Avg Render Time |
|-------|------|--------------|---------------|-----------------|
| FANTASY | 20 | 100.0% | 77.5/100 | 15.00s |
| ANIME | 20 | 85.0% | 65.2/100 | 33.23s |
| ACTION | 20 | 90.0% | 69.8/100 | 15.46s |
| ADVENTURE | 20 | 95.0% | 71.1/100 | 15.21s |
| MYSTERY | 20 | 100.0% | 76.4/100 | 15.10s |

## Detailed Logs (First 30 runs shown)
| ID | Genre | Status | Quality Score | Duration | Render Time | Error / Failure Type |
|----|-------|--------|---------------|----------|-------------|----------------------|
| 1 | FANTASY | PASS | 87 | 3.58s | 24.82s | None |
| 2 | ANIME | PASS | 87 | 3.58s | 16.21s | None |
| 3 | ACTION | PASS | 80 | 3.58s | 16.16s | None |
| 4 | ADVENTURE | PASS | 77 | 3.58s | 16.39s | None |
| 5 | MYSTERY | PASS | 77 | 3.58s | 17.67s | None |
| 6 | FANTASY | PASS | 72 | 1.79s | 8.22s | None |
| 7 | ANIME | PASS | 72 | 1.79s | 8.11s | None |
| 8 | ACTION | PASS | 72 | 1.79s | 7.56s | None |
| 9 | ADVENTURE | PASS | 72 | 1.79s | 8.14s | None |
| 10 | MYSTERY | PASS | 72 | 1.79s | 11.07s | None |
| 11 | FANTASY | PASS | 87 | 3.58s | 20.23s | None |
| 12 | ANIME | PASS | 80 | 3.58s | 22.41s | None |
| 13 | ACTION | PASS | 87 | 3.58s | 20.65s | None |
| 14 | ADVENTURE | PASS | 80 | 3.58s | 27.47s | None |
| 15 | MYSTERY | PASS | 87 | 3.58s | 15.34s | None |
| 16 | FANTASY | PASS | 72 | 1.79s | 7.81s | None |
| 17 | ANIME | PASS | 72 | 1.79s | 9.15s | None |
| 18 | ACTION | PASS | 72 | 1.79s | 10.06s | None |
| 19 | ADVENTURE | PASS | 72 | 1.79s | 9.19s | None |
| 20 | MYSTERY | PASS | 72 | 1.79s | 8.72s | None |
| 21 | FANTASY | PASS | 80 | 3.58s | 18.63s | None |
| 22 | ANIME | FAIL | N/A | 0.00s | 25.24s | HTTP 500 |
| 23 | ACTION | FAIL | N/A | 0.00s | 31.09s | HTTP 500 |
| 24 | ADVENTURE | FAIL | N/A | 0.00s | 25.91s | HTTP 500 |
| 25 | MYSTERY | PASS | 80 | 3.58s | 25.09s | None |
| 26 | FANTASY | PASS | 77 | 3.58s | 24.89s | None |
| 27 | ANIME | PASS | 77 | 3.58s | 32.62s | None |
| 28 | ACTION | FAIL | N/A | 0.00s | 25.53s | HTTP 500 |
| 29 | ADVENTURE | PASS | 77 | 3.58s | 17.50s | None |
| 30 | MYSTERY | PASS | 80 | 3.58s | 19.00s | None |
