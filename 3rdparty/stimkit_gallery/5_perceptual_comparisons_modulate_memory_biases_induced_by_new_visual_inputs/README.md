# Perceptual Comparisons Modulate Memory Biases — Stimuli Reproduction

This folder contains a stimkit-based reproduction of the trial-level stimuli used in
"Perceptual comparisons modulate memory biases induced by new visual inputs" (Saito et al., 2022).

## Quick Start

```bash
uv sync
uv run python "script/reproduce_stimuli.py"
```

Outputs are written to `output/` and organized by experiment, task type, and participant file.
Adjust `script/stimuli_config.toml` to change rendering limits or geometry assumptions.
