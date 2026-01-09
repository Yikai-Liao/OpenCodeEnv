# Gallery: The Object as the Unit for State Switching in VWM

This project is a reproduction of the stimuli and experimental logic from the research paper: **"The Object as the Unit for State Switching in Visual Working Memory"**. 

It demonstrates the use of the `stimkit` library to programmatically generate complex psychological experimental stimuli with high precision and reproducibility.

## 🌟 Overview

The experiments investigate whether the "unit" for switching representational states in Visual Working Memory (VWM) is an individual **feature** or the entire **object**. By manipulating whether features (like color and shape) belong to the same object (**Integrated**) or different objects (**Separate**), the study tests theories of VWM architecture.

### Key Experiments Reproduced
1.  **Experiment 1: Color-Shape Binding** — Integrated (colored shape) vs. Separate (colored circle + black shape).
2.  **Experiment 2: Same-Dimension Binding** — Integrated (bicolor circle) vs. Separate (two semicircles).
3.  **Experiment 3: Gestalt Binding** — Integrated (Kanizsa-like closure) vs. Separate (broken closure).

---

## 📂 Project Structure

```text
.
├── data/               # Behavioral raw data (.mat files) from the original paper.
│   └── README.md       # Detailed explanation of data columns and coding.
├── script/             # Core reproduction logic.
│   ├── reproduce_stimuli.py  # Main script to generate all stimuli images.
│   ├── stimuli_config.toml   # Central configuration for geometry, colors, and rendering.
│   ├── config.py             # Pydantic models for configuration and data schema.
│   └── inspect_mat.py        # Utility to inspect raw .mat data.
├── output/             # Generated stimuli images (automatically created).
├── paper/              # Paper text and reference figures.
└── exp_design.md       # Detailed technical specification of the reproduction.
```

---

## 🚀 Getting Started

This project uses `uv` for modern, fast Python dependency management.

### 1. Installation

Clone this repository and navigate to this gallery item:

```bash
cd gallery/1_object_as_unit
uv sync
```

### 2. Reproduce Stimuli

Run the main reproduction script to generate stimuli based on the original trial data:

```bash
uv run script/reproduce_stimuli.py
```

This will:
- Read the configuration from `script/stimuli_config.toml`.
- Load representative trials from the `data/` directory.
- Generate high-quality images (SVG/PNG) in the `output/` directory, organized by experiment, group, and phase.

---

## 🛠 Configuration

The reproduction is strictly governed by `script/stimuli_config.toml`. You can easily adjust:
- **Canvas**: Screen size, resolution, viewing distance ($D_{view}$), and background color.
- **Rendering**: Number of trials per condition, output format, and random seeds.
- **Geometry**: Item sizes, offsets, notch angles, and search array radius.
- **Visual Palette**: Precise mappings for the 5 colors and 5 shapes used in the experiment.

---

## 📖 Documentation

For a deep dive into the mathematical and geometric definitions used in this reproduction, see:
- [**Experimental Design & Geometric Definitions**](exp_design.md)
- [**Data Structure Details**](data/README.md)

---

## 📚 References

- **Paper Title**: *The Object as the Unit for State Switching in Visual Working Memory*
- **Authors**: Zhao, Y., Chen, H., et al.
- **Gallery Implementation**: Built with `stimkit`.
