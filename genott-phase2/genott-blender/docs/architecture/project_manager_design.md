# Movie Project Manager Design

## Purpose
Establishes an object-oriented manager that represents the film project as a hierarchical structure of acts, scenes, and shots referenced strictly by UUIDs.

## Responsibilities
* **Version Control Stack**: Maintains a history of changes (undo/redo stack) for non-destructive screenplay editing.
* **Persistent Serialization**: Saves and loads the project configurations to `movie_project/project.json`.
* **UUID Mapping**: Resolves logical scene and shot components using UUID indices rather than hardcoded filenames.

## Public Interfaces
```python
class MovieProjectManager:
    def create_project(self, script_path: str) -> str
    def save_project(self) -> None
    def add_shot(self, scene_id: str, shot_data: dict) -> str
    def undo_last_action(self) -> dict
```

## Dependencies
* `ai/timeline_editing.py`: Timestamps mapping.
* `database.py`: SQL tables integration.

## Data Flow
```
[Screenplay] -> [MovieProjectManager] -> [UUID Scene Registry] -> [Version History Stack] -> [project.json]
```

## Testing Strategy
* Verify project initialization generates valid UUID strings.
* Assert that the undo/redo stack pops historical states correctly.
