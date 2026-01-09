# Experiment Design: Boolean Maps as the Units of Working Memory Manipulation

## 1. Goal & Core Hypothesis

**Core Question:** Is the basic unit of working memory manipulation an **object** or a **Boolean map** (i.e., a feature-defined set)?

**Paper Summary (Psychological Science, 2024):**
- Experiments 1-2 manipulate **colors** (dyeing/moving multicolored objects).
- Experiments 3-4 manipulate **orientations** (moving/dyeing oriented bars).
- If manipulation operates on **Boolean maps**, manipulation time should increase with the number of **feature maps**, not the number of **objects**.

Reference: `paper/paper.md`, sections "Experiment 1-4: Method/Stimuli".

---

## 2. Data Availability & Reconstruction Policy

**Available data:** `data/ManipulationUnit-Data-All.xlsx` contains per-trial **condition codes** and behavioral measures (RT/accuracy), but **no trial-level item parameters** (no per-item positions, colors, orientations, or RNG seeds).

**Reconstruction strategy (deterministic):**
- We **synthesize** trial stimuli using a fixed RNG seed while **preserving all condition-level constraints** (Boolean map count, object count, orientation category, change/consistency flags).
- This satisfies the user requirement: "only the critical hypothesis-related constraints must be honored; exact colors/positions may be random with a fixed seed."

**Determinism:** seed = `20241221` (configurable in `script/stimuli_config.toml`).

---

## 3. Common Rendering Conventions

**Coordinate system:** All size/spacing parameters start in visual degrees (deg) and are converted once to canvas units before any layout/movement logic. Rendering uses `stimkit.VisualAngle` for conversion.

**Canvas:**
- Screen distance: 57 cm
- Screen size: 27"
- Resolution (assumed): 1920x1080

**Color palette (cue colors from paper):**
- Red #ff0000, Green #00ff00, Blue #0000ff, Pink #fa96c8, Yellow #ffff00, Cyan #00ffff, Dark Cyan #006464

**Output:** SVG files per trial and phase (Memory, Cue, Mask, Test).
- **Mask phase:** A 500ms mask consisting of a grid of multicolored items containing all feature values currently being memorized/manipulated, ensuring erasure of iconic memory.

---

## 4. Experiment 1 - Dyeing Multicolored Dumbbells

**Paper stimulus constraints:**
- Dumbbell ends: radius 1 deg
- Connector: length 5 deg, width 0.1 deg
- Item centers located at 2.83 deg eccentricity
- Orientation: horizontal vs vertical (per trial)

**Reconstruction details:**
- **Objects:** 2 dumbbells, centered at (0, +2.83 deg) and (0, -2.83 deg).
- **Ends:** two colored circles per dumbbell; orientation controls whether ends are left/right or top/bottom.
- **Cue:** colored rings on the ends to be dyed.
- **Manipulation:** cue colors overwrite the cued ends.

**Condition mapping (from `conditions`):**
- **1B1O:** cue both ends of one dumbbell, same color -> 1 Boolean map, 1 object.
- **1B2O:** cue one end from each dumbbell with the same color -> 1 Boolean map, 2 objects.
- **2B1O:** cue both ends of one dumbbell with different colors -> 2 Boolean maps, 1 object.
- **2B2O:** cue one end from each dumbbell with different colors -> 2 Boolean maps, 2 objects.

**Consistency (`consis`):**
- 0: test display equals manipulated array.
- 1: **cued ends** changed (color mismatch).
- 2: **uncued ends** changed.

---

## 5. Experiment 2 - Moving Multicolored Circles

**Paper stimulus constraints:**
- 4 circles in a 4x4 grid, cell size 2.5 deg
- Radius 0.8 deg
- Two single-color circles share the same color; two circles are bicolored (split).
- Orientation column defines left/right vs top/bottom split.

**Reconstruction details:**
- **Objects:** 4 circles arranged in a 2x2 block (positions: +/-1.25 deg in x/y).
- **Color composition:** 2 solid circles of color A; 2 split circles of colors A/B.
- **Cue:** black rings around the cued objects.
- **Manipulation:** cued items shift to nearest empty grid cell (deterministic rule).

**Condition mapping (`conditions`):**
- **1B1O:** cue a single solid circle (1 color, 1 object).
- **1B2O:** cue both solid circles (1 color, 2 objects).
- **2B1O:** cue one bicolor circle (2 colors, 1 object).
- **2B2O:** cue one solid and one bicolor circle (2 colors, 2 objects).

**Consistency (`consis`):**
- 0: test display equals manipulated array.
- 1: cued objects' colors changed (swap or re-color).
- 2: uncued objects' colors changed.
- 3: uncued **solid** objects' colors changed.
- 4: cued objects' positions incorrect (use original positions).

---

## 6. Experiment 3 - Moving Multiple Orientations

**Paper stimulus constraints:**
- 6 oriented bars in a 4x4 grid
- Colors: red/green/blue
- Orientations: +/-45 deg
- Subset size (2/3/4) and subset type (SCMO/MCSO/MCMO)
- Direction cue: up/down/left/right

**Reconstruction details:**
- **Positions:** 6 of 16 grid cells (deterministically sampled).
- **Cue:** black rings around cued bars.
- **Manipulation:** cued bars shift by one grid cell in the given direction.

**Subset type mapping (`color_orientation_type`):**
- **SCMO (1):** single color, multiple orientations among cued items.
- **MCSO (2):** multiple colors, single orientation among cued items.
- **MCMO (3):** multiple colors, multiple orientations among cued items.

**Probe change (`probe_change`, `change_attribute`):**
- 1: no change (test equals manipulated).
- 2: change one cued item's **color** or **orientation** or **position**.

---

## 7. Experiment 4 - Dyeing Multiple Orientations

**Paper stimulus constraints:**
- Black oriented bars on gray background
- Bar length 1.6 deg, width 0.2 deg
- Orientation: +/-45 deg
- Cue radius 0.8 deg

**Reconstruction details:**
- **Positions:** 8 bars sampled from the 4x4 grid.
- **Cue:** colored rings indicate dye color for cued bars.
- **Manipulation:** cued bars are dyed (color change).

**Condition mapping (`condition`):**
- **SCSO (1):** single color, single orientation.
- **SCMO (2):** single color, multiple orientations.
- **MCSO (3):** multiple colors, single orientation.
- **MCMO (4):** multiple colors, multiple orientations.

**Consistency (`consis`):**
- 0: test equals manipulated.
- 1: cued colors wrong.
- 2: cued orientations wrong.
- 3: uncued orientations wrong.
- 4: uncued colors wrong.

---

## 8. Outputs & Usage

**Script:** `script/reproduce_stimuli.py`

**Output layout:**
```
output/
  E1/subject_XX/Trial_0001_Memory.svg
  E1/subject_XX/Trial_0001_Cue.svg
  E1/subject_XX/Trial_0001_Mask.svg
  E1/subject_XX/Trial_0001_Test.svg
  E2/...
  E3/...
  E4/...
```

**Run (all trials):**
```
python script/reproduce_stimuli.py --exp all
```

**Preview (first N trials per subject):**
```
python script/reproduce_stimuli.py --max-trials 2
```

---

## 9. Assumptions Summary (Explicit)

- Exact per-trial item parameters are **not available** in the dataset; stimuli are generated to satisfy condition constraints.
- Movement direction is only known for Experiment 3; Experiment 2 uses a deterministic, condition-consistent movement rule.
- The reproduction prioritizes **Boolean-map vs object conditions** and **consistency manipulations**, matching the paper's logic.
