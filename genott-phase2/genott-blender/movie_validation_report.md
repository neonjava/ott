# Movie Validation Report

## Summary
| Metric | Value |
|--------|-------|
| Total Movies | 10 |
| Successful | 0 |
| Failed | 10 |
| Avg Duration | 0.00s |
| Avg Assembly Time | 0.00s |

## Individual Results
| Movie | Status | Time | Duration | Scenes | File | Video | Audio | Playable |
|-------|--------|------|----------|--------|------|-------|-------|----------|
| 1 | EXCEPTION | 0.0s | 0.0s | - | ❌ | ❌ | ❌ | ❌ |
| 2 | EXCEPTION | 0.0s | 0.0s | - | ❌ | ❌ | ❌ | ❌ |
| 3 | EXCEPTION | 0.0s | 0.0s | - | ❌ | ❌ | ❌ | ❌ |
| 4 | EXCEPTION | 0.0s | 0.0s | - | ❌ | ❌ | ❌ | ❌ |
| 5 | EXCEPTION | 0.0s | 0.0s | - | ❌ | ❌ | ❌ | ❌ |
| 6 | EXCEPTION | 0.0s | 0.0s | - | ❌ | ❌ | ❌ | ❌ |
| 7 | EXCEPTION | 0.0s | 0.0s | - | ❌ | ❌ | ❌ | ❌ |
| 8 | EXCEPTION | 0.0s | 0.0s | - | ❌ | ❌ | ❌ | ❌ |
| 9 | EXCEPTION | 0.0s | 0.0s | - | ❌ | ❌ | ❌ | ❌ |
| 10 | EXCEPTION | 0.0s | 0.0s | - | ❌ | ❌ | ❌ | ❌ |

## Most Common Failure
`HTTPConnectionPool(host='127.0.0.1', port=5001): Max retries exceeded with url: /api/generate-movie (Caused by NewConnectionError("HTTPConnection(host='127.0.0.1', port=5001): Failed to establish a new connection: [Errno 111] Connection refused"))` (10x)

## Conclusion
**10 movies failed validation. See details above.**
