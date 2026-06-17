# Final Benchmark Report (100 Movies E2E Test)

## Core Metrics
| Metric | Value |
|--------|-------|
| Success Rate | 97.0% |
| Total Movies Run | 100 |
| Successful Generations | 97 |
| Quality Engine Rejections | 0 |
| Pipeline Failures | 3 |
| Average Movie Duration | 2.68s |
| Average Render Time | 21.23s |
| Average Quality Score | 74.3/100 |
| Most Common Failure | RENDER |
| Total Benchmark Time | 2122.92s |

## Failure Category Breakdown
| Category | Failures Tracked | Description |
|----------|------------------|-------------|
| Render Failures | 2 | General exceptions, network timeouts, unhandled crashes |
| Blender Failures | 1 | Blender daemon crashes, scene building errors |
| FFmpeg Failures | 0 | Stitching / concatenation / audio merge failures |
| Audio Failures | 0 | Edge-TTS speech generation problems |
| Transition Failures | 0 | Invalid transition processing between scenes |
| Continuity Failures | 0 | Scene continuity or character matching discrepancies |

## Genre Analysis
| Genre | Runs | Success Rate | Average Score | Avg Render Time |
|-------|------|--------------|---------------|-----------------|
| FANTASY | 20 | 100.0% | 77.5/100 | 14.03s |
| ANIME | 20 | 100.0% | 76.4/100 | 14.67s |
| ACTION | 20 | 100.0% | 78.1/100 | 16.06s |
| ADVENTURE | 20 | 100.0% | 75.1/100 | 14.48s |
| MYSTERY | 20 | 85.0% | 64.5/100 | 46.90s |

## Detailed Logs (First 30 runs shown)
| ID | Genre | Status | Quality Score | Duration | Render Time | Error / Failure Type |
|----|-------|--------|---------------|----------|-------------|----------------------|
| 1 | FANTASY | PASS | 87 | 3.58s | 19.58s | None |
| 2 | ANIME | PASS | 87 | 3.58s | 31.98s | None |
| 3 | ACTION | PASS | 80 | 3.58s | 18.31s | None |
| 4 | ADVENTURE | PASS | 77 | 3.58s | 15.43s | None |
| 5 | MYSTERY | PASS | 77 | 3.58s | 24.11s | None |
| 6 | FANTASY | PASS | 72 | 1.79s | 7.71s | None |
| 7 | ANIME | PASS | 72 | 1.79s | 8.01s | None |
| 8 | ACTION | PASS | 72 | 1.79s | 10.98s | None |
| 9 | ADVENTURE | PASS | 72 | 1.79s | 6.55s | None |
| 10 | MYSTERY | PASS | 72 | 1.79s | 8.66s | None |
| 11 | FANTASY | PASS | 87 | 3.58s | 19.38s | None |
| 12 | ANIME | PASS | 80 | 3.58s | 18.41s | None |
| 13 | ACTION | PASS | 87 | 3.58s | 19.05s | None |
| 14 | ADVENTURE | PASS | 80 | 3.58s | 36.40s | None |
| 15 | MYSTERY | PASS | 87 | 3.58s | 18.95s | None |
| 16 | FANTASY | PASS | 72 | 1.79s | 16.67s | None |
| 17 | ANIME | PASS | 72 | 1.79s | 7.40s | None |
| 18 | ACTION | PASS | 72 | 1.79s | 12.25s | None |
| 19 | ADVENTURE | PASS | 72 | 1.79s | 8.00s | None |
| 20 | MYSTERY | PASS | 72 | 1.79s | 9.11s | None |
| 21 | FANTASY | PASS | 80 | 3.58s | 18.14s | None |
| 22 | ANIME | PASS | 80 | 3.58s | 16.25s | None |
| 23 | ACTION | PASS | 80 | 3.58s | 21.40s | None |
| 24 | ADVENTURE | PASS | 80 | 3.58s | 17.70s | None |
| 25 | MYSTERY | PASS | 80 | 3.58s | 16.44s | None |
| 26 | FANTASY | PASS | 77 | 3.58s | 24.07s | None |
| 27 | ANIME | PASS | 77 | 3.58s | 18.02s | None |
| 28 | ACTION | PASS | 87 | 3.58s | 16.31s | None |
| 29 | ADVENTURE | PASS | 77 | 3.58s | 21.62s | None |
| 30 | MYSTERY | PASS | 80 | 3.58s | 17.56s | None |
