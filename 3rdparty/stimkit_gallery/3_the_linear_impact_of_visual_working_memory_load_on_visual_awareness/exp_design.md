# Experiment Design: The Linear Impact of Visual Working Memory Load on Visual Awareness

## 1. Experiment Overview & Rationale

**Core Question:**
This study investigates whether and how Visual Working Memory (VWM) load modulates visual awareness.
> "investigating whether and how visual awareness is influenced by VWM load." (paper/paper.md, Abstract)

**Hypothesis:**
VWM load has a linear modulation effect on visual awareness. Specifically, higher VWM load leads to prolonged latency of Motion-Induced Blindness (MIB).
> "latency of MIB was prolonged gradually as the VWM load increased, revealing a linear trend" (paper/paper.md, Abstract)

**Experimental Logic:**
Participants perform a VWM task (memorizing shapes) and a concurrent MIB task (monitoring a target's disappearance).
1.  **Memory Prime:** Participants memorize 0, 1, 2, or 3 shapes.
2.  **MIB Task:** A global moving pattern (rotating blue crosses) and a target (yellow disc) appear. Participants press a key when the target disappears (MIB).
3.  **Memory Probe:** After MIB, participants judge if a probe display matches the memory prime (Change Detection).

**Experiments:**
*   **Experiment 1:** VWM Load (0, 1, 2, 3 items) vs MIB Latency.
*   **Experiment 2:** Replicate Exp 1 (Load 1, 3) and control for response speed using a "Physical Disappearance" condition.
*   **Experiment 3:** Control for low-level visual differences by having participants *count* items (1, 2, 3) instead of memorizing them.

### Experiment Flowchart

```mermaid
graph TD
    A[Start Trial] --> B[Fixation<br/>200ms]
    B --> C[Memory Prime<br/>2000ms<br/>(0, 1, 2, or 3 Shapes)]
    C --> D[MIB Display<br/>Until Response/Time]
    D -- Target Disappears --> E[Key Press (Report Invisibility)]
    D -- Target Reappears --> E
    E --> F[Blank<br/>1000ms]
    F --> G[Memory Probe<br/>Until Response]
    G --> H[Feedback<br/>500ms]
```
Source: paper/paper.md, Section 2.1 Procedure and Design; Fig. 1b.

---

## 2. Rigorous Geometric Definitions of Stimuli

**Coordinate System**:
*   Coordinates $(x, y)$ in **visual degrees ($^\circ$)** relative to screen center $(0,0)$.
*   **Screen**: 17-inch CRT, 1024x768 px, 75Hz. Viewing distance = 57 cm.
    > "17 in CRT monitor with a resolution of 1024 × 768 pixels... Viewing distance was fixed at 57 cm" (paper/paper.md, Methods 2.1)

### 2.1 Constants & Parameters

| Symbol | Config Key | Value | Description / Source |
| :--- | :--- | :--- | :--- |
| **Canvas** | | | |
| $S_{diag}$ | `screen_size` | 17.0 in | Screen diagonal size. |
| $R_{screen}$ | `screen_resolution` | (1024, 768) | Screen resolution (px). |
| $D_{view}$ | `screen_distance` | 57.0 cm | Viewing distance. |
| $C_{bg}$ | `bg_color` | "black" | Background color (implied by white fixation/yellow target). |
| **Fixation** | | | |
| $D_{fix}$ | `fixation_size` | $0.38^\circ$ | Diameter of circle / Size of cross. |
| Memory/Probe | **Cross** | - | > "contained a central fixation cross" (paper/paper.md, Methods 2.1) |
| MIB Phase | **Circle** | - | > "central white fixation point (a 0.38◦ circle... stroke of 1 pixel)" |
| $W_{fix}$ | `fixation_stroke` | 1 px | Stroke width of fixation point. |
| $C_{fix}$ | `fixation_color` | "white" | Color of fixation. |
| **MIB Display** | | | |
| $S_{mask}$ | `mask_size` | $17.62^\circ$ | Size of the grid of crosses. > "uniform array of 7 × 7 blue ... crosses (17.62◦ × 17.62◦)" |
| $N_{cross}$ | `grid_dims` | (7, 7) | Grid dimensions (7x7). |
| $C_{cross}$ | `cross_color` | (50, 50, 255) | Color of crosses (RGB). > "blue (RGB:50/50/255)" |
| $S_{cross}$ | `cross_size` | $\approx 0.8^\circ$ | Size of individual crosses. **Estimated from Fig 2b**. |
| $W_{cross}$ | `cross_width` | $\approx 0.15^\circ$ | Stroke width of crosses. **Estimated from Fig 2b**. |
| $\omega_{rot}$ | `rotation_speed` | $240^\circ/s$ | Rotation speed of crosses (Clockwise). > "rotated clockwise at 240◦/s" (Snapshot angle is randomized per trial in reproduction). |
| $D_{target}$ | `target_size` | $0.50^\circ$ | Diameter of target disc. > "bright yellow target object disc (0.50◦)" |
| $P_{target}$ | `target_pos` | $(-2.06, 2.06)$* | Target position (Upper-Left). Derived from $2.91^\circ$ distance. $\sqrt{x^2+y^2}=2.91$. Assuming 45° angle in UL quadrant implies $x = -2.91/\sqrt{2} \approx -2.06$. > "upper-left quadrant... 2.91◦ from the fixation point" |
| $C_{target}$ | `target_color` | "yellow" | Color of target. |

*\*Note on Target Position:* $2.91^\circ$ distance in upper-left. Assuming 45 deg diagonal: $x = -2.91 * \cos(45^\circ) \approx -2.06^\circ$, $y = 2.91 * \sin(45^\circ) \approx 2.06^\circ$.

### 2.2 Memory Display
*   **Items:** 0, 1, 2, or 3 shapes randomly chosen from 6 meaningless shapes.
*   **Locations:** 4 possible locations (Top, Bottom, Left, Right of a diamond).
    *   Top: $(0, 4.18)$
    *   Bottom: $(0, -4.18)$
    *   Left: $(-4.18, 0)$
    *   Right: $(4.18, 0)$
    > "Each shape was presented at one of the four corners of an invisible diamond... each corner placed 4.18◦ from the central fixation."
*   **Load Conditions:**
    *   Load 0: No shapes.
    *   Load 1: 1 shape at a random location.
    *   Load 2: 2 shapes at random distinct locations.
    *   Load 3: 3 shapes at random distinct locations.

### 2.3 MIB Display
*   **Fixation:** Center $(0,0)$.
*   **Mask:** 7x7 grid of rotating crosses centered at $(0,0)$.
*   **Target:** Yellow disc at Upper-Left.

### 2.4 Probe Display
*   Same locations as Memory Prime.
*   **Match:** Identical shapes.
*   **Mismatch:** One shape changed to a different one from the set (not present in prime).

---

## 3. Data Structure (`.txt` Files)

Files are located in `data/data/exp1/`, `data/data/exp2/`, `data/data/exp3/`.
Format: Space-separated text files.

**Columns:**
1.  `Trial`: Trial number.
2.  `Condition`: Experimental Condition (See mapping below).
3.  `RT1`: MIB Latency (Time to report disappearance).
4.  `RT2`: MIB Duration (Duration of disappearance).
5.  `RT3`: Memory Probe RT.
6.  `Acc`: Memory Probe Accuracy (1=Correct, 0=Incorrect).
7.  `KeyResponse`: Key pressed.

### Condition Mapping

#### Experiment 1
| Value | Load | Probe Match |
| :--- | :--- | :--- |
| **1** | 1 Item | Same |
| **2** | 1 Item | Different |
| **3** | 2 Items | Same |
| **4** | 2 Items | Different |
| **5** | 3 Items | Same |
| **6** | 3 Items | Different |
| **7** | 0 Items | N/A |
| **8** | 0 Items | N/A |

#### Experiment 2 (MIB Part)
Replicates Exp 1 but only Load 1 and Load 3.
| Value | Load | Probe Match |
| :--- | :--- | :--- |
| **1** | 1 Item | Same |
| **2** | 1 Item | Different |
| **3** | 3 Items | Same |
| **4** | 3 Items | Different |

#### Experiment 3
Counting Task (No memory match/mismatch).
| Value | Number of Items |
| :--- | :--- |
| **1** | 1 Item |
| **2** | 2 Items |
| **3** | 3 Items |
