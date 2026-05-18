from osgeo import gdal
import geopandas as gpd
import pandas as pn
import numpy as np
import rasterio as rio
import matplotlib.pyplot as plt
import os


#processing data

def differencing(raster1,
                 raster2,
                 clip_area,
                 tr_x,
                 tr_y,
                 clip_layer_name,
                 output_dir,
                 resampling_method: str = "bilinear"):
   
   """
   Takes two DSMs (.tif) and a clip area (.shp) and computes the difference between both models. Resampl 
   Outputs a raster later with each pixel value representing the difference.
   """

   raster1_name = os.path.splitext(os.path.basename(raster1))[0]
   folder_name = clip_layer_name[:-8] + "_" + raster1_name[:-4]
   
   newpath = output_dir + clip_layer_name[:-8]
   if not os.path.exists(newpath):
      os.makedirs(newpath)
   
   print("Calculating DOM for ", clip_layer_name[:-8])

   #setting output paths

   raster1_resampled = newpath + "\\" + os.path.splitext(os.path.basename(raster1))[0] + '_resampled.tif'
   raster2_resampled = newpath + "\\" + os.path.splitext(os.path.basename(raster2))[0] + '_resampled.tif'

   raster1_clip = newpath + "\\" + os.path.splitext(os.path.basename(raster1))[0] + '_clip.tif'
   raster2_clip = newpath + "\\" + os.path.splitext(os.path.basename(raster2))[0] + '_clip.tif'


   #resample rasters to the same resolution
   resampling_method = "bilinear"
   
   resample(raster1_resampled, raster1, tr_x, tr_y, resampling_method)
   resample(raster2_resampled, raster2, tr_x, tr_y, resampling_method)

   #clip rasters to the same clip_area
   clip(raster1_clip, raster1_resampled, clip_area, clip_layer_name)
   clip(raster2_clip, raster2_resampled, clip_area, clip_layer_name)


   #difference preprocessed rasters
   
   differenced_output = newpath + "\\" + "differenced_" + os.path.splitext(os.path.basename(raster1))[0] + os.path.splitext(os.path.basename(raster2))[0] + '.tif'

   raster_subtract(raster1_clip, raster2_clip, differenced_output)

   return differenced_output

def resample(out_path, src_ds, tr_x, tr_y, resample):
    gdal.Warp(out_path, src_ds,
              xRes=tr_x, yRes=tr_y,
              targetAlignedPixels = True,
              resampleAlg=resample)

def clip(out_path, src_ds, shapefile, clip_layer_name):
    gdal.Warp(out_path, src_ds,
              format='GTiff', cutlineDSName = shapefile,
              cutlineLayer = clip_layer_name,
              cropToCutline=True,
              dstNodata = -2222)

def raster_subtract(raster1_clip, raster2_clip, out_path):
   
   #read the rasters with rasterio
   raster1 = rio.open(raster1_clip)
   r1 = raster1.read(1, masked = True)
   raster2 = rio.open(raster2_clip)
   r2 = raster2.read(1, masked = True)


   #difference the rasters
   subtracted = r2 - r1

   # get the crs and transform from one of the rasters
   with rio.open(raster2_clip) as src:
      dsm_transform = src.transform
      dsm_crs = src.crs
      band1 = src.read(1)
      
      dsm_height, dsm_width = band1.shape

      #write metadata to save new raster
      metadata_dsm = {
         'driver': 'GTiff',
         'count': 1,
         'dtype': 'float32',
         'width': dsm_width,
         'height': dsm_height,
         'crs': dsm_crs,
         'transform': dsm_transform
         }

      with rio.open(out_path, 'w', **metadata_dsm) as rast:
         rast.write(subtracted, 1)

      return out_path


def calculate_vol_loss(model, no_data: int = -2222):
    """
    Takes a differenced drone model (.tif) and calculates the total volume loss and carbon released.
    Model needs to be projected to UTM for units to be in metres
    """
    with rio.open(model) as src:
        band1 = src.read(1, masked = True)
        band1.data[band1.data == no_data] = 0

        X_res, Y_res = src.res #meters/pixel
        print(X_res, Y_res)

        sum_of_all_values = np.sum(band1)
        sum_of_vol_loss = np.sum(band1[band1 < 0])
        sum_of_deposited = np.sum(band1[band1 > 0])
        
        pixel_area = abs(X_res * Y_res)

        #total area divided by resolution = 
        volume_change = pixel_area * sum_of_all_values
        vol_loss = np.abs(pixel_area * sum_of_vol_loss)
        vol_deposited = np.abs(pixel_area * sum_of_deposited)
        print(f"Total volume change: {volume_change:.2f}", f"Total volume lost: {vol_loss:.2f}",f"Total vol deposited: {vol_deposited:.2f}",)


#example use
"""
EastIceCALDs_4Aug2024 = r"Data\EastIceCALDs_4Aug2024_DSM.tif" #change later to reprojected version
EastIceCALDs_30Jun2024 = r"Data\EastIceCALDs_30Jun2024_DSM.tif"
EIC_cut = r'Data\EastIceCreekLower_cutline.shp'

differencing(EastIceCALDs_30Jun2024, EastIceCALDs_4Aug2024, EIC_cut, 0.08, 0.08, 'EastIceCreekLower_cutline')

"""