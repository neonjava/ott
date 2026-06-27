# Final Benchmark Report (100 Movies E2E Test)

## Core Metrics
| Metric | Value |
|--------|-------|
| Success Rate | 100.0% |
| Total Movies Run | 100 |
| Successful Generations | 100 |
| Quality Engine Rejections | 0 |
| Pipeline Failures | 0 |
| Average Movie Duration | 9.43s |
| Average Render Time | 77.30s |
| Average Quality Score | 80.5/100 |
| Most Common Failure | NONE |
| Total Benchmark Time | 7730.48s |

## Failure Category Breakdown
| Category | Failures Tracked | Description |
|----------|------------------|-------------|
| Render Failures | 0 | General exceptions, network timeouts, unhandled crashes |
| Blender Failures | 0 | Blender daemon crashes, scene building errors |
| FFmpeg Failures | 0 | Stitching / concatenation / audio merge failures |
| Audio Failures | 0 | Edge-TTS speech generation problems |
| Transition Failures | 0 | Invalid transition processing between scenes |
| Continuity Failures | 0 | Scene continuity or character matching discrepancies |

## Genre Analysis
| Genre | Runs | Success Rate | Average Score | Avg Render Time |
|-------|------|--------------|---------------|-----------------|
| FANTASY | 20 | 100.0% | 81.5/100 | 78.27s |
| ANIME | 20 | 100.0% | 80.0/100 | 77.38s |
| ACTION | 20 | 100.0% | 82.1/100 | 75.73s |
| ADVENTURE | 20 | 100.0% | 78.7/100 | 78.23s |
| MYSTERY | 20 | 100.0% | 80.4/100 | 76.91s |

## Detailed Logs (First 30 runs shown)
| ID | Genre | Status | Quality Score | Duration | Render Time | Error / Failure Type |
|----|-------|--------|---------------|----------|-------------|----------------------|
| 1 | FANTASY | PASS | 92 | 4.05s | 83.02s | None |
| 2 | ANIME | PASS | 90 | 6.66s | 80.81s | None |
| 3 | ACTION | PASS | 85 | 5.55s | 81.05s | None |
| 4 | ADVENTURE | PASS | 82 | 5.59s | 79.89s | None |
| 5 | MYSTERY | PASS | 82 | 5.42s | 87.88s | None |
| 6 | FANTASY | PASS | 75 | 2.54s | 75.41s | None |
| 7 | ANIME | PASS | 75 | 2.15s | 77.88s | None |
| 8 | ACTION | PASS | 75 | 1.91s | 74.99s | None |
| 9 | ADVENTURE | PASS | 75 | 2.08s | 81.29s | None |
| 10 | MYSTERY | PASS | 75 | 1.87s | 75.02s | None |
| 11 | FANTASY | PASS | 92 | 4.86s | 79.07s | None |
| 12 | ANIME | PASS | 85 | 15.00s | 83.78s | None |
| 13 | ACTION | PASS | 92 | 12.63s | 80.13s | None |
| 14 | ADVENTURE | PASS | 85 | 6.27s | 80.65s | None |
| 15 | MYSTERY | PASS | 92 | 5.50s | 79.27s | None |
| 16 | FANTASY | PASS | 75 | 2.90s | 75.23s | None |
| 17 | ANIME | PASS | 75 | 2.92s | 80.50s | None |
| 18 | ACTION | PASS | 75 | 3.55s | 72.80s | None |
| 19 | ADVENTURE | PASS | 75 | 9.71s | 77.22s | None |
| 20 | MYSTERY | PASS | 75 | 2.97s | 74.04s | None |
| 21 | FANTASY | PASS | 85 | 4.74s | 80.78s | None |
| 22 | ANIME | PASS | 85 | 10.00s | 75.66s | None |
| 23 | ACTION | PASS | 85 | 21.67s | 75.87s | None |
| 24 | ADVENTURE | PASS | 83 | 17.67s | 79.34s | None |
| 25 | MYSTERY | PASS | 85 | 4.05s | 76.41s | None |
| 26 | FANTASY | PASS | 82 | 16.58s | 81.58s | None |
| 27 | ANIME | PASS | 80 | 20.92s | 77.41s | None |
| 28 | ACTION | PASS | 92 | 9.17s | 78.21s | None |
| 29 | ADVENTURE | PASS | 82 | 10.33s | 77.63s | None |
| 30 | MYSTERY | PASS | 85 | 16.42s | 75.25s | None |
