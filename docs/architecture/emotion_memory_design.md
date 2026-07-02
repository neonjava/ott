# Emotion Memory Engine Subsystem Design

## Purpose
Maintain persistent character emotional status coordinates (happiness, anger, sadness, fear) across scenes, simulating emotional memory, decay, and reactions to narrative stimuli.

## Responsibilities
* **Baseline Persistence**: Maintain baseline emotional vectors per character.
* **Stimulus Processing**: Apply adjustments to active vectors based on narrative keywords/inputs (e.g., getting attacked increases anger).
* **Decay Calculations**: Apply mathematical decay rates to return spikes toward baseline values over scene durations.

## Public Interfaces
```python
class EmotionMemoryEngine:
    def process_stimulus(self, char_id: str, stimulus: str) -> Dict[str, float]
    def tick_decay(self, char_id: str, time_delta: float) -> Dict[str, float]
```

## Dependencies
* `character_state_manager.py`: Persists dynamic profile entries.
* `ai/dialogue_performance.py`: Reads baseline emotional shifts to update speech pacing.

## Data Flow
```
[Dialogue or Action Stimulus] -> [process_stimulus] -> [Emotion Vectors Updated] -> [tick_decay] -> [Character Profile State Saved]
```

## Testing Strategy
* Test stimulus boosts for various keywords.
* Verify linear/exponential decay calculations return values toward baseline over simulated intervals.
