# Experiment Design: Perceptual Comparisons Modulate Memory Biases

## 1. Overview

**Goal.** Compare how explicit perceptual comparisons (Compare Task) modulate memory biases relative to tasks where the probe is **ignored** (Exp. 1) or **remembered** (Exp. 2), across **color** and **shape** feature spaces.

**Experiments.**
- **Exp. 1A (color)**: Compare vs. Ignore tasks.
- **Exp. 1B (shape)**: Compare vs. Ignore tasks.
- **Exp. 2A (color)**: Compare vs. Remember tasks.
- **Exp. 2B (shape)**: Compare vs. Remember tasks.

**Core manipulation.** Probe items are sampled ±30°, ±60°, or ±90° away from the memory item on a circular feature space. Baseline trials contain no probe.

## 2. Stimulus Definitions (from paper)

### 2.1 Color space (Exp. 1A, 2A)
- **Color wheel:** 360 equally spaced values in CIE L\*a\*b\*.
- **Center:** a\* = 20, b\* = 38. **Radius:** 60. **L\*:** 70.
- **Memory / probe item:** circular color patch, **200 px** diameter.
- **Color wheel:** **800 px** diameter; each color value occupies 1°; wheel is **randomly rotated** per trial.

### 2.2 Shape space (Exp. 1B, 2B)
- **Shape space:** 360 shapes on a circular similarity continuum (Li et al., 2020).
- **Memory / probe item:** **200 × 200 px**.
- **Shape wheel:** 18 equidistant exemplar shapes on an **800 px** diameter circle; wheel is **randomly rotated** per trial.

**Note:** The original Li et al. (2020) shape set is not included in the dataset. The reproduction script uses a deterministic radial‑frequency generator to approximate the 360-shape continuum. See section 5.

## 3. Trial Procedure (behavioral timing; summarized)

**Block structure:** Each task consists of **5 blocks × 32 trials**, with baseline and experimental trials pseudorandomized within each block.

**Baseline trials (all tasks, 25%)**
1. Memory item (1000 ms)
2. Delay (2000 ms)
3. Memory report on wheel → confidence

**Experimental trials (75%)**
1. Memory item (1000 ms)
2. Delay (500 ms)
3. Probe item (1000 ms)
4. Delay (500 ms)
5. Memory report on wheel → confidence
6. Task-specific follow-up:
   - **Compare Task (Exp. 1 & 2):** Similarity judgment after a "2" prompt.
   - **Ignore Task (Exp. 1):** No follow-up report.
   - **Remember Task (Exp. 2):** Second memory report (probe item), indicated by "2".

**Exp. 2 note:** The numbers "1" and "2" are displayed during the first and second report screens, respectively, to reduce reporting the wrong item.

(Exact timings are in paper/paper.md; the reproduction script focuses on the visual stimuli for each phase.)

## 4. Trial-Level Data Mapping (verified from `.mat` files)

Each `.mat` file contains **trial-level data** for a single participant. The MATLAB variable name matches the file prefix.

### 4.1 Common fields
- `block` (1–5)
- `trial` (1–32)
- `target1_stim_index` → **Memory item index** (1–360)
- `target2_stim_index` → **Probe item index** (1–360; see baseline rules)
- `test` → **Probe distance condition** (see below)
- `current_dir` → **Probe direction** (1 = + / clockwise, 2 = − / counter‑clockwise)
- `final_resp1`, `final_confidence1` → Response metadata (not required for stimulus rendering)

### 4.2 Exp. 1 (Ignore / Compare)
Files:
- `inter_color_ignore_data_XX.mat`
- `inter_color_recog_data_XX.mat`
- `inter_shape_ignore_data_XX.mat`
- `inter_shape_recog_data_XX.mat`

`test` encoding (verified):
- `1` = baseline (no probe; `target2_stim_index = -1`)
- `2` = ±30°
- `3` = ±60°
- `4` = ±90°

Additional field in Compare data:
- `recog_resp` (1 = similar, 2 = dissimilar, −1 = baseline)

### 4.3 Exp. 2 (Remember / Compare)
Files:
- `inter_color_recall_data_XX.mat`
- `inter_color_recog_data_XX.mat`
- `inter_shape_recall_data_XX.mat`
- `inter_shape_recog_data_XX.mat`

`test` encoding (verified):
- `0` = baseline (no probe; `final_resp2 = 0`, `final_confidence2 = −2`)
- `1` = ±30°
- `2` = ±60°
- `3` = ±90°

For baseline trials in Exp. 2, `target2_stim_index` is present but equals `target1_stim_index`. The reproduction script treats `test == 0` as **no probe**.

## 5. Rendering Assumptions (documented)

1. **Display geometry:** The paper does not report a fixed screen size for Exp. 1 (remote) and does not give a specific monitor size for Exp. 2. The reproduction uses **24" / 1920×1080 / 60 cm** to convert pixel sizes to canvas units.
2. **Color wheel thickness:** Not specified. The reproduction renders a **ring** (default 80 px thickness) to avoid occluding the center.
3. **Shape space:** The Li et al. (2020) shapes are not provided. We use a deterministic radial‑frequency generator to approximate a continuous 360‑shape wheel. This preserves the circular index structure, but **does not perfectly match** the original stimulus set. Shapes are rendered as **outline-only** to match the figure examples.
4. **Report prompts:** For Exp. 2, the script overlays "1" on the first report wheel and "2" on the second report wheel (or prompt screen for Compare). Prompts are omitted on baseline trials without a probe.
5. **Wheel rotation:** The data do not record trial‑level wheel rotations. Rotations are randomized per trial using a fixed seed in `script/stimuli_config.toml`.

## 6. Output Organization

Rendered files are stored under:

```
output/{Experiment}/{task_type}/{participant_file}/Trial_{n}_{phase}.svg
```

Phases rendered by default:
- `Memory`
- `Probe`
- `Wheel1`
- `Prompt`
- `Wheel2`

This mirrors the primary visual stimuli while keeping the sequence modular.
