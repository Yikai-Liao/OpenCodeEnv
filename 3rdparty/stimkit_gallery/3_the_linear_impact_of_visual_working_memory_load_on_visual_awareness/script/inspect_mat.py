import scipy.io
import sys
from pathlib import Path
import numpy as np

def inspect_mat(file_path):
    print(f"Inspecting: {file_path}")
    try:
        mat = scipy.io.loadmat(file_path)
        print("Keys:", mat.keys())
        for key in mat:
            if key.startswith('__'): continue
            val = mat[key]
            print(f"Key: {key}, Type: {type(val)}")
            if isinstance(val, np.ndarray):
                print(f"  Shape: {val.shape}, Dtype: {val.dtype}")
                if val.size < 20:
                    print(f"  Data: {val}")
                else:
                    print(f"  Data (first 5 rows):\n{val[:5]}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_mat.py <path_to_mat_file>")
        sys.exit(1)
    inspect_mat(sys.argv[1])
