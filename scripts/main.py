import numpy as np
import rasterio as rio







# Create a clean, isolated environment with python 3.10 and rasterio
conda create -n greenland_env -c conda-forge python=3.10 rasterio -y

# Activate your new environment
conda activate greenland_env

pip install pygmtsar

conda activate greenland_env
conda install -c conda-forge numba llvmlite -y
pip install pygmtsar
