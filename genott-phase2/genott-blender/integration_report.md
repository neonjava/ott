# Full Pipeline Integration Report

## Summary
- **Test Script Input**: "An exhausted knight loses hope in the forest. A dragon appears and teaches him courage. Together they return to the kingdom."
- **Multiple Scenes Generated**: PASSED (Count: 4)
- **Character Interactions Detected**: PASSED
- **Emotion Changes Mapped**: PASSED (Unique moods: neutral, sad, determination)
- **Logical Timeline Maintained**: PASSED (Events: event_1, event_2, event_3, event_4)
- **Storyboard Quality Score**: 110/100
- **Overall Pipeline Status**: **SUCCESS**

## Stage-by-Stage Details

### 1. Story Understanding Engine (Extracted Entities)
- **Characters**: [{"name": "knight", "modifiers": ["exhausted"]}, {"name": "dragon", "modifiers": []}]
- **Locations**: [{"name": "forest", "modifiers": []}, {"name": "kingdom", "modifiers": []}]
- **Objects**: [{"name": "hope", "modifiers": ["loses"]}]
- **Timeline**: ["event_1", "event_2", "event_3", "event_4"]

### 2. Scene Planner V2 Output
- **Raw Scene Plans**:
```json
[
  {
    "scene_number": 1,
    "character_name": "knight",
    "location": "forest",
    "action": "idle",
    "camera_shot": "close-up helmet shot",
    "duration": 4.0,
    "dialogue": null,
    "narration": "An exhausted knight loses hope in the forest",
    "visual_description": "The knight is seen performing idle in the forest. Target is hope.",
    "mood": "sad",
    "speed": "normal"
  },
  {
    "scene_number": 2,
    "character_name": "dragon",
    "location": "forest",
    "action": "idle",
    "camera_shot": "cinematic wide",
    "duration": 4.0,
    "dialogue": null,
    "narration": "A dragon appears",
    "visual_description": "The dragon is seen performing idle in the forest.",
    "mood": "neutral",
    "speed": "normal"
  },
  {
    "scene_number": 3,
    "character_name": "dragon",
    "location": "forest",
    "action": "idle",
    "camera_shot": "cinematic wide",
    "duration": 4.0,
    "dialogue": null,
    "narration": "teaches him courage",
    "visual_description": "The dragon is seen performing idle in the forest.",
    "mood": "determination",
    "speed": "normal"
  },
  {
    "scene_number": 4,
    "character_name": "dragon",
    "location": "kingdom",
    "action": "idle",
    "camera_shot": "cinematic wide",
    "duration": 4.0,
    "dialogue": null,
    "narration": "Together they return to the kingdom",
    "visual_description": "The dragon is seen performing idle in the kingdom.",
    "mood": "neutral",
    "speed": "normal"
  }
]
```

### 3. Emotion Engine Enrichments
- **Scene-level Emotional Parameters**:
```json
[
  {
    "scene_number": 1,
    "character_name": "knight",
    "location": "forest",
    "action": "idle",
    "camera_shot": "close-up helmet shot",
    "duration": 4.0,
    "dialogue": null,
    "narration": "An exhausted knight loses hope in the forest",
    "visual_description": "The knight is seen performing idle in the forest. Target is hope.",
    "mood": "sad",
    "speed": "normal",
    "facial_expression": "frown",
    "animation_override": "CharacterArmature|Idle",
    "facial_parameters": {
      "eyebrow_raise": -0.2,
      "mouth_frown": 1.0
    },
    "focal_length": 85.0,
    "shake_amplitude": 0.01,
    "dof_aperture": 1.4
  },
  {
    "scene_number": 2,
    "character_name": "dragon",
    "location": "forest",
    "action": "idle",
    "camera_shot": "cinematic wide",
    "duration": 4.0,
    "dialogue": null,
    "narration": "A dragon appears",
    "visual_description": "The dragon is seen performing idle in the forest.",
    "mood": "neutral",
    "speed": "normal",
    "facial_expression": "neutral",
    "animation_override": "CharacterArmature|Idle",
    "facial_parameters": {},
    "focal_length": 50.0,
    "shake_amplitude": 0.0,
    "dof_aperture": 5.6
  },
  {
    "scene_number": 3,
    "character_name": "dragon",
    "location": "forest",
    "action": "idle",
    "camera_shot": "cinematic wide",
    "duration": 4.0,
    "dialogue": null,
    "narration": "teaches him courage",
    "visual_description": "The dragon is seen performing idle in the forest.",
    "mood": "determination",
    "speed": "normal",
    "facial_expression": "focused",
    "animation_override": "CharacterArmature|Sword_Slash",
    "facial_parameters": {
      "eyebrows_down": 0.5,
      "mouth_closed": 1.0,
      "eyes_narrow": 0.4
    },
    "focal_length": 50.0,
    "shake_amplitude": 0.05,
    "dof_aperture": 2.0
  },
  {
    "scene_number": 4,
    "character_name": "dragon",
    "location": "kingdom",
    "action": "idle",
    "camera_shot": "cinematic wide",
    "duration": 4.0,
    "dialogue": null,
    "narration": "Together they return to the kingdom",
    "visual_description": "The dragon is seen performing idle in the kingdom.",
    "mood": "neutral",
    "speed": "normal",
    "facial_expression": "neutral",
    "animation_override": "CharacterArmature|Idle",
    "facial_parameters": {},
    "focal_length": 50.0,
    "shake_amplitude": 0.0,
    "dof_aperture": 5.6
  }
]
```

### 4. Director AI Output
- **Directed Storyboard (Transitions, Pacing, Cameras)**:
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "character_name": "knight",
      "location": "forest",
      "action": "idle",
      "camera_shot": "establishing_shot",
      "duration": 5.5,
      "dialogue": null,
      "narration": "An exhausted knight loses hope in the forest",
      "visual_description": "The knight is seen performing idle in the forest. Target is hope.",
      "mood": "sad",
      "speed": "normal",
      "facial_expression": "frown",
      "animation_override": "CharacterArmature|Idle",
      "facial_parameters": {
        "eyebrow_raise": -0.2,
        "mouth_frown": 1.0
      },
      "focal_length": 85.0,
      "shake_amplitude": 0.01,
      "dof_aperture": 1.4,
      "camera_movement": "static",
      "pacing": "slow",
      "transition": "cut"
    },
    {
      "scene_number": 2,
      "character_name": "dragon",
      "location": "forest",
      "action": "idle",
      "camera_shot": "wide_shot",
      "duration": 4.5,
      "dialogue": null,
      "narration": "A dragon appears",
      "visual_description": "The dragon is seen performing idle in the forest.",
      "mood": "neutral",
      "speed": "normal",
      "facial_expression": "neutral",
      "animation_override": "CharacterArmature|Idle",
      "facial_parameters": {},
      "focal_length": 50.0,
      "shake_amplitude": 0.0,
      "dof_aperture": 5.6,
      "camera_movement": "static",
      "pacing": "standard",
      "transition": "cut"
    },
    {
      "scene_number": 3,
      "character_name": "dragon",
      "location": "forest",
      "action": "idle",
      "camera_shot": "wide_shot",
      "duration": 4.5,
      "dialogue": null,
      "narration": "teaches him courage",
      "visual_description": "The dragon is seen performing idle in the forest.",
      "mood": "determination",
      "speed": "normal",
      "facial_expression": "focused",
      "animation_override": "CharacterArmature|Sword_Slash",
      "facial_parameters": {
        "eyebrows_down": 0.5,
        "mouth_closed": 1.0,
        "eyes_narrow": 0.4
      },
      "focal_length": 50.0,
      "shake_amplitude": 0.05,
      "dof_aperture": 2.0,
      "camera_movement": "static",
      "pacing": "standard",
      "transition": "cut"
    },
    {
      "scene_number": 4,
      "character_name": "dragon",
      "location": "kingdom",
      "action": "idle",
      "camera_shot": "wide_shot",
      "duration": 4.5,
      "dialogue": null,
      "narration": "Together they return to the kingdom",
      "visual_description": "The dragon is seen performing idle in the kingdom.",
      "mood": "neutral",
      "speed": "normal",
      "facial_expression": "neutral",
      "animation_override": "CharacterArmature|Idle",
      "facial_parameters": {},
      "focal_length": 50.0,
      "shake_amplitude": 0.0,
      "dof_aperture": 5.6,
      "camera_movement": "static",
      "pacing": "standard",
      "transition": "fade"
    }
  ],
  "transitions": [
    "cut",
    "cut",
    "fade"
  ]
}
```

### 5. Quality Verification
- **Score**: 110/100
- **Camera Diversity Score**: 10/15 (Shots used: wide_shot, establishing_shot)
- **Environment Diversity Score**: 15/15 (Locations used: forest, kingdom)
- **Transition Quality Score**: 15/15 (Transitions: cut, cut, fade)
- **Continuity and Scene Count Score**: 30/30
