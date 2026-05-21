import rasterio as rio
import geopandas as gpd
import os
from matplotlib import pyplot as plt
from osgeo import gdal
import rasterstats
from rasterstats import zonal_stats
import numpy as np


U_2017_2024_path = "data/Unstable_2017_2024.shp"
DEM_path = "data/Ataa_2025_DEM_clip.tif"
slope_path = "data/Ataa_2025_Slope.tif"
aspect_path = "data/Ataa_2025_Aspect.tif"

# Read data and view
U_2017_2024 = gpd.read_file(U_2017_2024_path)

#print(U_2017_2024.head())

# Load DEM
DEM_src = rio.open(DEM_path, masked = True)
DEM_affine = DEM_src.transform
DEM = DEM_src.read(1)

#slope = gdal.DEMProcessing(slope_path, DEM_path, 'slope')
slope = rio.open(slope_path)
slope = slope.read(1, masked =True)

#aspect = gdal.DEMProcessing(aspect_path, DEM_path, 'aspect')
aspect = rio.open(aspect_path)
aspect = aspect.read(1, masked =True)

# What area did the ALDs cover?
#print("Total area in km2", sum(U_2017_2024["area"]/1000000)) # 27596


# Dissolve ALDs to one feature
dissolved = U_2017_2024.dissolve()
#print(dissolved)

U_slope = zonal_stats(
    dissolved,
    slope_path,
    stats=["min", "max", "mean"]
)

# Total area in m2 27596
#print(U_slope) #[{'min': 0.030257781967520714, 'max': 79.98497009277344, 'mean': 21.28396609947215}

U_aspect = zonal_stats(
    dissolved,
    aspect_path,
    stats=["min", "max", "mean"])

U_elevation = zonal_stats(
    dissolved,
    DEM_path,
    stats=["min", "max", "mean"])

# Total area in m2 27596
#print("U ASPECT", U_aspect) # [{'min': 0.009352350607514381, 'max': 359.9530029296875, 'mean': 219.72018950198355}]
#print("U ELEVATION", U_elevation) #[[{'min': 30.7463436126709, 'max': 761.2211303710938, 'mean': 404.9478705616209}]
#print("U SLOPE", U_slope) #[[{'min': 0.030257781967520714, 'max': 79.98497009277344, 'mean': 21.28396609947215}]

df_slope = gpd.GeoDataFrame(U_slope).add_prefix('slope_')
df_aspect = gpd.GeoDataFrame(U_aspect).add_prefix('aspect_')
df_elev = gpd.GeoDataFrame(U_elevation).add_prefix('elev_')

U_2017_2024 = U_2017_2024.join([df_slope, df_aspect, df_elev])

print(U_2017_2024)


