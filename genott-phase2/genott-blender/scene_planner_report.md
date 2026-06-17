# Scene Planner V2 Benchmark Report

## Overview
- **Planner Version**: 2.0.0 (Rule-based Event-to-Scene Mapper)
- **Total Test Stories**: 100
- **Passed**: 100
- **Failed**: 0
- **Success Rate**: 100.0%
- **Total Execution Time**: 9.723 seconds

## Scene Generation Metrics
- **Total Scenes Generated**: 160 (Avg: 1.6/story)
- **Total Movie Planned Duration**: 656.5 seconds (Avg: 6.6 seconds/story)

### Camera Shot Distribution
- **cinematic wide**: 87
- **close-up helmet shot**: 22
- **rotating orbit shot around the character**: 20
- **close-up tracking shot**: 18
- **low-angle dramatic wide shot**: 13

### Action Distribution
- **idle**: 82
- **run**: 17
- **discover**: 12
- **attack**: 12
- **walk**: 11
- **wave**: 7
- **duck**: 6
- **enter**: 5
- **talk**: 5
- **help**: 1
- **jump**: 1
- **follow**: 1

### Mood/Emotion Distribution
- **neutral**: 51
- **fear**: 24
- **happy**: 23
- **sad**: 19
- **determination**: 16
- **angry**: 13
- **surprise**: 10
- **hope**: 4

## Detailed Results
| ID | Story | Status | Scenes Planned | Total Duration | Cameras Used | Actions Used |
|---|---|---|---|---|---|---|
| 1 | A lonely knight loses faith, discovers an ancient dragon, and regains purpose. | PASS | 3 | 12.0s | close-up helmet shot, cinematic wide, rotating orbit shot around the character | idle, discover |
| 2 | The brave mage enters the dark cave and prepares a magic spell. | PASS | 2 | 8.0s | cinematic wide | enter, idle |
| 3 | A tired robot slowly walks across the dry beach, searching for power. | PASS | 2 | 11.0s | cinematic wide | walk, idle |
| 4 | The happy princess joyfully waves from the tall tower. | PASS | 1 | 3.5s | rotating orbit shot around the character | wave |
| 5 | A terrified villager quickly flees from the forest as the beast roars. | PASS | 1 | 3.0s | close-up tracking shot | run |
| 6 | The angry warrior violently strikes the shield with a heavy sword. | PASS | 1 | 4.5s | low-angle dramatic wide shot | attack |
| 7 | An ancient dragon sleeps in the volcanic mountain, guarding the treasure. | PASS | 2 | 8.0s | cinematic wide | idle |
| 8 | The curious anime girl notices a glowing crystal on the hill. | PASS | 1 | 4.0s | rotating orbit shot around the character | discover |
| 9 | A mysterious wizard whispers a spell inside the ancient temple. | PASS | 1 | 5.0s | close-up helmet shot | talk |
| 10 | The proud prince victoriously stands on the battlefield, raising his crown. | PASS | 2 | 8.0s | cinematic wide | idle |
| 11 | A tiny fox cautiously crouching behind a bush in the snowy woods. | PASS | 1 | 4.0s | close-up helmet shot | duck |
| 12 | The combat android runs aggressively to attack the monster. | PASS | 1 | 3.0s | close-up tracking shot | run |
| 13 | A sad traveler sits by the lake, grieving a lost friend. | PASS | 2 | 8.0s | close-up helmet shot, cinematic wide | idle |
| 14 | The bold samurai slays the demon in the bamboo forest. | PASS | 1 | 4.5s | low-angle dramatic wide shot | attack |
| 15 | A terrified child hides in the dark room, trembling with fear. | PASS | 2 | 8.0s | close-up helmet shot, cinematic wide | idle, duck |
| 16 | The queen proudly greets the crowd in the kingdom plaza. | PASS | 1 | 3.5s | rotating orbit shot around the character | wave |
| 17 | A lonely shadow wanders through the ruins of the castle. | PASS | 1 | 5.0s | cinematic wide | walk |
| 18 | The ironman flies swiftly to save the falling city. | PASS | 1 | 4.0s | rotating orbit shot around the character | help |
| 19 | A determined elf shoots an arrow from the green field. | PASS | 1 | 4.0s | cinematic wide | idle |
| 20 | The furious hulk smashes the robot with extreme rage. | PASS | 1 | 4.5s | low-angle dramatic wide shot | attack |
| 21 | A peaceful merchant rests near the bridge, looking at the sky. | PASS | 2 | 8.0s | cinematic wide | idle |
| 22 | The tense ninja dodges the incoming shuriken in the night garden. | PASS | 1 | 4.0s | close-up helmet shot | duck |
| 23 | A happy couple walks along the shore, celebrating their victory. | PASS | 2 | 9.0s | cinematic wide | walk, idle |
| 24 | The ghost screams inside the abandoned house, causing panic. | PASS | 2 | 9.0s | close-up helmet shot, cinematic wide | idle, talk |
| 25 | A tired captain guides the crew through the storm to the island. | PASS | 1 | 4.0s | cinematic wide | idle |
| 26 | The brave knight charges aggressively at the enemy army. | PASS | 1 | 3.0s | close-up tracking shot | run |
| 27 | A lonely mage wanders inside the giant library, looking for a scroll. | PASS | 2 | 9.0s | cinematic wide | walk, idle |
| 28 | The proud warrior holds the legendary sword on the mountain top. | PASS | 1 | 4.0s | cinematic wide | idle |
| 29 | A frightened traveler runs through the swamp, escaping the beast. | PASS | 2 | 8.0s | close-up tracking shot | run |
| 30 | The cheerful anime boy waves to his friends from the boat. | PASS | 1 | 3.5s | rotating orbit shot around the character | wave |
| 31 | A furious giant attacks the stone wall with a giant hammer. | PASS | 1 | 4.5s | low-angle dramatic wide shot | attack |
| 32 | The curious girl discovers a secret door behind the old mirror. | PASS | 1 | 4.0s | rotating orbit shot around the character | discover |
| 33 | A tense guard stands at the castle gate, holding a spear. | PASS | 2 | 8.0s | cinematic wide | idle |
| 34 | The exhausted wizard regains hope after finding the ancient amulet. | PASS | 1 | 4.0s | rotating orbit shot around the character | discover |
| 35 | A sad prince weeps in the garden, losing all faith in his quest. | PASS | 2 | 8.0s | close-up helmet shot, cinematic wide | idle |
| 36 | The determined hero walks into the dungeon to face the demon. | PASS | 1 | 5.0s | cinematic wide | walk |
| 37 | A surprised child finds a chest of gold coins in the cave. | PASS | 1 | 4.0s | rotating orbit shot around the character | discover |
| 38 | The proud samurai stands victorious in the arena after the fight. | PASS | 1 | 4.5s | low-angle dramatic wide shot | attack |
| 39 | A terrified girl runs away from the shadow in the forest. | PASS | 1 | 4.0s | close-up tracking shot | run |
| 40 | The angry queen shouts orders to the guards, pointing to the gate. | PASS | 2 | 9.0s | close-up helmet shot, cinematic wide | idle, talk |
| 41 | A happy fox jumps around the meadow, chasing a butterfly. | PASS | 2 | 8.0s | close-up tracking shot, low-angle dramatic wide shot | follow, jump |
| 42 | The lonely traveler sits under the tree, looking at the map. | PASS | 2 | 8.0s | close-up helmet shot, cinematic wide | idle |
| 43 | A brave warrior protects the child with a steel shield. | PASS | 1 | 4.0s | cinematic wide | idle |
| 44 | The evil wizard cast a shadow over the peaceful village. | PASS | 1 | 4.0s | cinematic wide | idle |
| 45 | A surprised traveler spots an oasis in the dry desert. | PASS | 1 | 4.0s | rotating orbit shot around the character | discover |
| 46 | The tired robot rests on the rusty bridge, losing power. | PASS | 2 | 8.0s | cinematic wide | idle |
| 47 | A terrified captain flees from the sea monster, escaping in fear. | PASS | 2 | 8.0s | close-up tracking shot | run |
| 48 | The cheerful princess greets the travelers at the palace entry. | PASS | 1 | 3.5s | rotating orbit shot around the character | wave |
| 49 | A lonely dwarf searches for gold in the deep mine. | PASS | 1 | 4.0s | close-up helmet shot | idle |
| 50 | The aggressive robot attacks the base, destroying the defense. | PASS | 2 | 8.5s | cinematic wide, low-angle dramatic wide shot | idle, attack |
| 51 | A sad warrior grieves his fallen captain on the glacier. | PASS | 1 | 4.0s | close-up helmet shot | idle |
| 52 | The brave knight discovers the holy chalice inside the ruins. | PASS | 1 | 4.0s | rotating orbit shot around the character | discover |
| 53 | A tense mage crouches in the bushes, waiting for the guard. | PASS | 2 | 8.0s | close-up helmet shot, cinematic wide | idle, duck |
| 54 | The proud prince waves from the horse, entering the city. | PASS | 2 | 7.5s | cinematic wide, rotating orbit shot around the character | wave, enter |
| 55 | A lonely boy sits in the library, reading a dusty book. | PASS | 2 | 8.0s | close-up helmet shot, cinematic wide | idle |
| 56 | The furious beast charges aggressively, breaking the trees. | PASS | 2 | 7.0s | cinematic wide, close-up tracking shot | idle, run |
| 57 | A terrified villager hides inside the temple, praying for safety. | PASS | 2 | 8.0s | close-up helmet shot, cinematic wide | idle, duck |
| 58 | The happy traveler walks through the village, singing a song. | PASS | 2 | 9.0s | cinematic wide | walk, idle |
| 59 | A determined captain draws a sword, preparing for the battle. | PASS | 2 | 8.5s | cinematic wide, low-angle dramatic wide shot | idle, attack |
| 60 | The surprised queen notices a hidden letter in the drawer. | PASS | 1 | 4.0s | rotating orbit shot around the character | discover |
| 61 | A lonely wolf wanders through the snowy forest, seeking a pack. | PASS | 2 | 9.0s | cinematic wide | walk, idle |
| 62 | The brave warrior enters the cave, holding a burning torch. | PASS | 2 | 8.0s | cinematic wide | enter, idle |
| 63 | A tired mage rests by the campfire, regaining his energy. | PASS | 2 | 8.0s | cinematic wide | idle |
| 64 | The happy girl joyfully dances on the sandy beach. | PASS | 1 | 4.0s | cinematic wide | idle |
| 65 | A terrified soldier flees from the battlefield, losing his shield. | PASS | 2 | 8.0s | cinematic wide, close-up tracking shot | idle, run |
| 66 | The angry captain yells at the crew, demanding focus. | PASS | 2 | 9.0s | close-up helmet shot, cinematic wide | idle, talk |
| 67 | A proud knight stands on the hill, looking at the castle. | PASS | 2 | 8.0s | cinematic wide | idle |
| 68 | The curious prince finds a magic ring in the garden. | PASS | 1 | 4.0s | rotating orbit shot around the character | discover |
| 69 | A tense child crawls through the narrow tunnel, escaping the beast. | PASS | 2 | 8.0s | cinematic wide, close-up tracking shot | idle, run |
| 70 | The determined hero climbs the steep mountain, seeking the sage. | PASS | 2 | 8.0s | cinematic wide | idle |
| 71 | A sad queen walks along the river, mourning the king. | PASS | 2 | 9.0s | cinematic wide | walk, idle |
| 72 | The happy boy waves from the tower, celebrating the victory. | PASS | 2 | 7.5s | cinematic wide, rotating orbit shot around the character | wave, idle |
| 73 | A lonely mage discovers an ancient orb in the dark dungeon. | PASS | 1 | 4.0s | rotating orbit shot around the character | discover |
| 74 | The brave samurai stands in the arena, preparing to strike. | PASS | 2 | 8.5s | cinematic wide, low-angle dramatic wide shot | idle, attack |
| 75 | A terrified traveler runs into the castle, seeking shelter. | PASS | 2 | 8.0s | cinematic wide, close-up tracking shot | idle, run |
| 76 | The furious warrior attacks the dragon with a spear. | PASS | 1 | 4.5s | low-angle dramatic wide shot | attack |
| 77 | A happy fox rests in the green grass, enjoying the sun. | PASS | 2 | 8.0s | cinematic wide | idle |
| 78 | The lonely prince loses hope, sitting on the cold throne. | PASS | 2 | 8.0s | close-up helmet shot, cinematic wide | idle |
| 79 | A determined girl runs through the storm to save the wolf. | PASS | 1 | 4.0s | close-up tracking shot | run |
| 80 | The proud captain holds the map, declaring the destination. | PASS | 2 | 8.0s | cinematic wide | idle |
| 81 | A tense guard walks around the wall, checking the shadows. | PASS | 2 | 9.0s | cinematic wide | walk, idle |
| 82 | The surprised wizard notices the crystal glowing, feeling hope. | PASS | 2 | 8.0s | cinematic wide, rotating orbit shot around the character | idle, discover |
| 83 | A sad traveler weeps by the ruins, losing faith. | PASS | 2 | 8.0s | close-up helmet shot, cinematic wide | idle |
| 84 | The brave knight rescues the prince from the tower. | PASS | 1 | 4.0s | cinematic wide | idle |
| 85 | A terrified villager runs from the fire, escaping to the hill. | PASS | 2 | 8.0s | close-up tracking shot | run |
| 86 | The angry beast roars inside the cave, preparing to attack. | PASS | 2 | 8.5s | cinematic wide, low-angle dramatic wide shot | idle, attack |
| 87 | A happy princess waves to the soldiers, celebrating the peace. | PASS | 2 | 7.5s | cinematic wide, rotating orbit shot around the character | wave, idle |
| 88 | The lonely samurai walks through the desert, looking for a master. | PASS | 2 | 9.0s | cinematic wide | walk, idle |
| 89 | A determined warrior enters the arena, raising his shield. | PASS | 2 | 8.0s | cinematic wide | enter, idle |
| 90 | The proud queen stands before the throne, holding the scepter. | PASS | 2 | 8.0s | cinematic wide | idle |
| 91 | A tense mage whispers a spell, hiding behind the pillar. | PASS | 2 | 9.0s | close-up helmet shot | talk, duck |
| 92 | The surprised child spots a dragon flying in the sky. | PASS | 1 | 4.0s | rotating orbit shot around the character | discover |
| 93 | A sad robot sits in the rain, losing memory. | PASS | 2 | 8.0s | close-up helmet shot, cinematic wide | idle |
| 94 | The brave captain fights the pirate on the ship deck. | PASS | 1 | 4.5s | low-angle dramatic wide shot | attack |
| 95 | A terrified traveler flees the swamp, crying in fear. | PASS | 2 | 8.0s | close-up helmet shot, close-up tracking shot | idle, run |
| 96 | The furious robot smashes the terminal, causing an alarm. | PASS | 2 | 8.5s | cinematic wide, low-angle dramatic wide shot | idle, attack |
| 97 | A happy boy runs through the meadow, holding a kite. | PASS | 2 | 8.0s | cinematic wide, close-up tracking shot | idle, run |
| 98 | The lonely traveler walks through the cold forest, seeking warmth. | PASS | 2 | 9.0s | cinematic wide | walk, idle |
| 99 | A determined knight enters the castle ruins, seeking the sword. | PASS | 2 | 8.0s | cinematic wide | enter, idle |
| 100 | The proud wizard stands on the tower, watching the stars. | PASS | 2 | 8.0s | cinematic wide | idle |
