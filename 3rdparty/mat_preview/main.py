#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class Entry:
    name: str
    kind: str  # "dataset" | "variable" | "group" | "other"
    dtype: str
    shape: Tuple[int, ...]
    sample: Optional[str] = None
    note: Optional[str] = None


def is_hdf5_mat(path: str) -> bool:
    """
    Heuristic:
    - If h5py can open it, it's HDF5 (MAT v7.3 is HDF5).
    """
    try:
        import h5py  # type: ignore
    except Exception:
        return False

    try:
        with h5py.File(path, "r"):
            return True
    except Exception:
        return False


def _np_sample_str(arr: np.ndarray, k: int) -> str:
    if arr.ndim == 0:
        return np.array2string(arr, separator=", ")
    with np.printoptions(edgeitems=k, threshold=k, linewidth=120, suppress=True):
        flat = arr.ravel()
        s = flat[:k]
        return np.array2string(s, separator=", ")


def preview_hdf5(path: str, max_entries: int, sample_k: int) -> List[Entry]:
    import h5py  # type: ignore

    out: List[Entry] = []

    def add_entry(name: str, obj: Any) -> None:
        nonlocal out
        if len(out) >= max_entries:
            return

        if isinstance(obj, h5py.Dataset):
            dtype = str(obj.dtype)
            shape = tuple(int(x) for x in obj.shape)

            sample = None
            note = None
            try:
                arr = obj[()]
                a = np.asarray(arr)

                if a.dtype == object:
                    note = "object dtype; sample omitted"
                else:
                    sample = _np_sample_str(a, sample_k)
            except Exception as e:
                note = f"sample error: {type(e).__name__}"

            out.append(
                Entry(
                    name=name,
                    kind="dataset",
                    dtype=dtype,
                    shape=shape,
                    sample=sample,
                    note=note,
                )
            )
        elif isinstance(obj, h5py.Group):
            out.append(
                Entry(
                    name=name,
                    kind="group",
                    dtype="",
                    shape=(),
                    note=f"{len(obj)} members",
                )
            )

    with h5py.File(path, "r") as f:
        f.visititems(add_entry)

    return out


def preview_classic(path: str, max_entries: int, sample_k: int) -> List[Entry]:
    from scipy.io import loadmat  # type: ignore

    data = loadmat(path, struct_as_record=False, squeeze_me=True)
    out: List[Entry] = []

    for name, value in list(data.items())[:max_entries]:
        if name.startswith("__"):
            continue

        if isinstance(value, np.ndarray):
            dtype = str(value.dtype)
            shape = tuple(int(x) for x in value.shape)

            sample = None
            note = None
            try:
                if value.dtype == object:
                    note = "object dtype; sample omitted"
                else:
                    sample = _np_sample_str(value, sample_k)
            except Exception as e:
                note = f"sample error: {type(e).__name__}"

            out.append(
                Entry(
                    name=name,
                    kind="dataset",
                    dtype=dtype,
                    shape=shape,
                    sample=sample,
                    note=note,
                )
            )
        else:
            sample = None
            note = None
            try:
                sample = str(value)
            except Exception as e:
                note = f"sample error: {type(e).__name__}"

            out.append(
                Entry(
                    name=name,
                    kind="variable",
                    dtype=type(value).__name__,
                    shape=(),
                    sample=sample,
                    note=note,
                )
            )

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview .mat files")
    parser.add_argument("path", help="Path to .mat file")
    parser.add_argument(
        "-o", "--output", type=str, help="Output to file (default: stdout)"
    )
    parser.add_argument(
        "--max-entries", type=int, default=50, help="Maximum entries to show"
    )
    parser.add_argument(
        "--sample-k", type=int, default=5, help="Sample size for arrays"
    )
    args = parser.parse_args()

    if is_hdf5_mat(args.path):
        entries = preview_hdf5(args.path, args.max_entries, args.sample_k)
    else:
        entries = preview_classic(args.path, args.max_entries, args.sample_k)

    output = json.dumps([asdict(e) for e in entries], indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
