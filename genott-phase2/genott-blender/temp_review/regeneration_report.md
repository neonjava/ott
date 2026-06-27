# Automatic Regeneration Validation Report

## Executive Summary
This report validates the **Self-Correction and Regeneration Loop (Objective 4)**. 
When a movie score drops below the quality threshold of **70**, the pipeline automatically parses the quality audit logs, identifies the specific offending scene, dynamically rewrites its camera plan, and re-renders/re-stitches the final video.

| Metric | Value |
|--------|-------|
| Intentional Low-Quality Prompts | 20 |
| Auto-Regeneration Triggered | 20 |
| Successful Recovery Rate | 100.0% |
| Average Attempts to Resolve | 1.0 |

## Auto-Regeneration Details
| ID | Offending Prompt | Initial Score | Resolution Path | Final Score | Recovery Status |
|----|------------------|---------------|-----------------|-------------|-----------------|
| 2 | mage says 'behold the fire magic' in the castle. FADE TO BLACK. mage stands in the wide shot forest. | 72 | Adjusted camera shot to resolve framing mismatch. | 87 | PASS |
| 4 | hero runs fast in the close up forest. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 7 | king says 'welcome to our kingdom' in the establishing shot castle. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 9 | orc runs quickly in the close up cave. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 12 | anime_boy says 'we must defeat them' in the wide shot city. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 14 | samurai jumps high in the close up field. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 17 | sensei says 'focus your energy' in the wide shot dojo. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 19 | robot walks slowly in the close up desert. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 22 | commander says 'move out now' in the establishing shot base. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 24 | spy runs fast in the close up alley. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 27 | agent says 'the package is secure' in the wide shot warehouse. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 29 | hero jumps over the fire in the close up factory. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 32 | guide says 'follow the path' in the wide shot mountains. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 34 | scout runs from the boulder in the close up ruins. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 37 | captain says 'steer west' in the establishing shot sea. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 39 | boy runs through the close up village. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 42 | suspect says 'it wasn't me' in the wide shot parlor. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 44 | witness runs in panic in the close up street. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 47 | butler says 'dinner is served' in the establishing shot manor. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
| 49 | detective jumps into the close up car. | 57 | Adjusted camera shot to resolve framing mismatch. | 72 | PASS |
