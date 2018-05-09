#### Florian Beyers
### The script stacks Parrot Sequoia bands from a eBee Plus UAV flight
### with Python 2.7
## 2018-05-09

##### instructions
### 1. copy the script file to the directory where Pix4D saved the single bands
### 2. apply script in cmd (Windows) / bash (Linux) with '(sudo) python Stack_Ebee.py'
### 3. the stacked file appears in the same directory, called: 'stack.tif'

# import packages
from os import listdir, getcwd
from os.path import join
from osgeo import gdal
import numpy as np


#--------------- Functions...

def getMetadata(path, data):
    # get metadata
    
    ds = gdal.Open(join(path,data[0]))
    
    projection = ds.GetProjection()     # projection
    cols = ds.RasterXSize               # number of columns
    rows = ds.RasterYSize               # number of rows
    geoTransform = ds.GetGeoTransform()
    x_min = geoTransform[0]             # x-coord upper left corner
    y_max = geoTransform[3]             # y-coord upper left corner
    gsd = geoTransform[1]               # pixel size in meters
    
    return projection, cols, rows, x_min, y_max, gsd


def save_stack(name, arrays, meta):
    # STACK arrays and save data as TIFF in the same folder
    
    driver = gdal.GetDriverByName('GTiff') # load tiff properties
    stack = driver.Create(name,meta[1],meta[2],len(arrays),gdal.GDT_Float32, )
    stack.SetGeoTransform((meta[3],meta[5],0,meta[4],0,-meta[5]))
    stack.SetProjection(meta[0])
    for i in range(0,len(arrays)):
        stack.GetRasterBand(i+1).WriteArray(arrays[i])
    stack.FlushCache()

#----------------------------------------------------------------------------

print 'start processing!'

# directory where the Lansat data are stored
# load_path = "N:/Daten_GG/projekte/PFIFFikus (EFRE) - 74120125/Bilder/2018_05_04_Wetscapes/2018_05_04_CW_CD/2018_05_04_CW_CD_MS/2018_05_04_CW_CD_MS/4_index/reflectance"
load_path = str(getcwd())

print 'file directory: {}'.format(load_path)

# read tif files in directory 
allfiles = listdir(load_path)
temp = []
for i in allfiles:
    if i.endswith('.tif'):
        temp.append(i)
del(i)

print 'following bands are identified: \n{}'.format(temp)


# ordering files according to bands setting
bands_ordered = [0]*len(temp)
for i in range(0,len(temp)):
    if temp[i].endswith('green.tif'):
        bands_ordered[0] = temp[i]        
    elif temp[i].endswith('red.tif'):
        bands_ordered[1] = temp[i]
    elif temp[i].endswith('red edge.tif'):
        bands_ordered[2] = temp[i]
    elif temp[i].endswith('nir.tif'):
        bands_ordered[3] = temp[i]
    else:
        print 'Error!'

print 'data set re-ordered: \n{}'.format(bands_ordered)

# read raster bands as numpy arrays
bands = []
for i in range(0,len(bands_ordered)):
    # open tif with gdal
    ds = gdal.Open(join(load_path,bands_ordered[i]))
    # read band as array
    band = np.array(ds.GetRasterBand(1).ReadAsArray())
    bands.append(band)
    del(band,i)


# set negative values to zero
for i in bands:
    i[i<0] = 0

# read meta data
meta = getMetadata(load_path,bands_ordered)


# save stacked data set
filename = join(load_path,'stack.tif')

save_stack(filename, bands, meta)

print 'Images stacked successfully!'