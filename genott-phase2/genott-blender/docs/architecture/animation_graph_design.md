# Animation Graph & Blend Tree Subsystem Design

## Purpose
Enable characters to transition smoothly between distinct animation clips (e.g., idle, walk, run, jump) without visual popping, supporting procedural animation blending and state-machine transitions.

## Responsibilities
* **State Machine Management**: Maintain active character animation states and compute valid state transitions based on locomotion velocity and script triggers.
* **Blend Tree Processing**: Calculate weighted combinations of multiple animation source frames (e.g., blending 30% walk and 70% run for a fast walk).
* **Bone Transform Interpolation**: Provide linear and spherical linear interpolation matrices between skeletal frames.

## Public Interfaces
```python
class AnimationGraph:
    def update_state(self, current_state: str, velocity: float) -> str
    def evaluate_blend(self, state: str, speed: float) -> Dict[str, float]
```

## Internal Components
* `LocomotionStateMachine`: Transition loops for character actions.
* `BlendTreeEvaluator`: Evaluates relative active weight coefficients for animation tracks.

## Dependencies
* `ai/motion_intelligence.py`: Fetches locomotion pace profiles.
* `ai/scene_graph.py`: Modifies relative transform nodes.

## Data Flow
```
[Actor Script Speed] -> [LocomotionStateMachine] -> [BlendTreeEvaluator] -> [Active Blend Weights Dictionary] -> [Blender Daemon Keyframing]
```

## Future Extensibility
Support dynamic Inverse Kinematics (IK) constraint overlays (like foot-ground alignment) as post-processing layers on top of blended bone transforms.

## Testing Strategy
* Unit test weight calculations under various speeds (0.0 to 3.0 m/s).
* Integration verification to ensure correct transition state paths are navigated.

## Potential Risks
* Performance overhead when evaluating large blend trees (hundreds of joints) in Python. Mitigated by outsourcing final weight matrices to Blender's native Action blending layers.
