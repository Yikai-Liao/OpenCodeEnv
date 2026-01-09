
import scipy.io
import numpy as np
import os

file_path = "/home/lyk/code/stim_example/gallery/1_object_as_unit/data/Exp1/Integrated_group/caoyifang.mat"

try:
    mat = scipy.io.loadmat(file_path)
    print("Keys:", mat.keys())
    for key in mat:
        if not key.startswith('__'):
            data = mat[key]
            print(f"Key: {key}, Type: {type(data)}, Shape: {data.shape if hasattr(data, 'shape') else 'N/A'}")
            if hasattr(data, 'shape') and data.size < 100:
                 print(data)
            elif hasattr(data, 'shape') and len(data.shape) == 2:
                 print(f"First row: {data[0, :]}")

except Exception as e:
    print(f"Failed with scipy: {e}")
    try:
        import h5py
        with h5py.File(file_path, 'r') as f:
            print("Keys (h5py):", list(f.keys()))
            for key in f.keys():
                print(f"Key: {key}, Shape: {f[key].shape}")
    except Exception as e2:
        print(f"Failed with h5py: {e2}")
