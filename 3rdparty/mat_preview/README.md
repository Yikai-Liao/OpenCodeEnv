# MAT Preview

Preview .mat files from command line.

## Installation

```bash
pip install mat-preview
```

Or build from source:

```bash
uv build
uv pip install dist/mat_preview-0.1.0-py3-none-any.whl
```

## Usage

Preview a .mat file and output JSON to stdout:

```bash
mat_preview path/to/file.mat
```

Output to a file:

```bash
mat_preview path/to/file.mat -o output.json
```

Limit number of entries:

```bash
mat_preview path/to/file.mat --max-entries 10
```

Control sample size:

```bash
mat_preview path/to/file.mat --sample-k 20
```

## Supported Formats

- Classic MAT files (MATLAB v4, v6, v7)
- MAT v7.3 files (HDF5 format)
