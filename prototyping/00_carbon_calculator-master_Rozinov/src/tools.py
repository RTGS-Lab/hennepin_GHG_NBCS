import io
import base64

import shapely
import rasterio
import threading
import numpy as np
import pandas as pd
import geopandas as gpd
import rioxarray as rxr
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

######################################
#        Dashboard backend           #
#Computes updated sequestration rates#
######################################

#1. Recursive function creating all possible combinations for the given sequestration rates and landcover classes
def recursive_wrapper(data, initial_depth): #depth 0-7
    l = [None]*(initial_depth+1)
    D, k = {}, 0
    def recursive(data, depth):
        nonlocal l 
        nonlocal k
        if depth > -1:
            sub = data[depth]
            depth -= 1
            for index, row in sub.iterrows():
                l[depth+1] = row
                if depth == -1 and len(l) == len(data):
                    D[k] = pd.DataFrame(l.copy())
                    k+=1
                recursive(data, depth)

    recursive(data, initial_depth)
    return D

#2. Counter function, processing the results of the created combinations
def count(data, nlcd_pixels, standard_r):
    storages, seqs = [], []
    counted = Counter(nlcd_pixels)
    R = recursive_wrapper(data, 7)
    for i in range(len(R)):
        df=R[i]
        st, sq = 0, 0
        for key in counted:
            if key!=0:
                st+=counted[key]*df[df.land_cover==standard_r[key]].storage.item()
                sq+=counted[key]*df[df.land_cover==standard_r[key]].sequestration.item()
        st /= sum(counted.values())
        sq /= sum(counted.values())
        storages.append(st)
        seqs.append(sq)
    return storages, seqs

#3. Convert geojson geometry (polygon) to a shapely object
def geojson_to_shapely(drawn_features):
    shapely_geometries = []
    for feature in drawn_features['features']:
        geom = feature['geometry']['coordinates']
        shapely_geometries.append(shapely.geometry.Polygon(geom[0]))
    return shapely_geometries

#4. Calculate total seq and storage for the whole area using the user updated landcover map
def calculate_carbon(drawn_features, classes):
    classes = [int(x) for x in classes if x in ['0', '1', '2', '3', '4', '5', '6', '7', '8']]
    polygons = geojson_to_shapely(drawn_features)

    raster = rxr.open_rasterio("./nlcd_reclas.tif") #NLCD dataset reclassified for the current project

    gdf = gpd.GeoDataFrame({'geometry': polygons}, crs="EPSG:4326") #geodataframe with the drawn polygons
    gdf = gdf.to_crs("EPSG:4326")

    transform = raster.rio.transform() 
    out_shape = (raster.shape[1], raster.shape[2])  
    gdf = gdf.to_crs("EPSG:4326")
    raster.rio.write_crs("EPSG:4326", inplace=True)
    shapes = [[shape] for shape in gdf.geometry]
    for idx, shape in enumerate(shapes):
        #Rasterizing the drawings (convertin from a set of vector polygons to a set of masks, e.g. rasters)
        rasterized_mask = rasterio.features.rasterize( 
            shape, 
            out_shape=out_shape,
            transform=transform,
            fill=0,
            dtype=np.uint8
        )
        rasterized_mask = np.where((raster[0] != 0), rasterized_mask, 0) #making it a binary mask
        if idx==0:
            masked = raster[0].where(rasterized_mask==0, other=classes[idx]) 
        else:
            masked = masked.where(rasterized_mask==0, other=classes[idx]) #merging all the mask into one

    #Uploading pre-processed inventory rates (to create various scenario combinations)    
    for i in range(1,4):
        if 'df' not in locals():
            df = pd.read_csv(f'./data/Inventory_{i}.csv')
        else:
            df_new = pd.read_csv(f'./data/Inventory_{i}.csv')
            df = pd.concat([df, df_new]).reset_index(drop=True)

    data=[]
    for label, group in df.groupby('land_cover'): #splitting all rates based on land cover into groups
        data.append(group) 

    standard = {
        'None': 0,
        'Agro': 1,
        'Forest': 2,
        'Shrub': 3,
        'Wetland': 4,
        'Grassland': 5,
        'Urban': 6,
        'Sparsely vegetated': 7,
        'Heathland': 8,
    }
    standard_r = {v: k for k, v in standard.items()}

    nlcd_pixels = masked.values.flatten()

    #Computing new storage and sequestration distribution
    storages, seqs = count(data, nlcd_pixels, standard_r)
    carbon_nlcd = pd.DataFrame(columns=['storage', 'sequestration'])
    carbon_nlcd.storage = storages
    carbon_nlcd.sequestration = seqs
    custom_cmap = [
        (0, (0.0, 0.0, 0.0, 0.0)),            
        (1, 'yellow'),       
        (2, 'darkgreen'),      
        (3, 'green'),           
        (4, 'brown'),         
        (5, 'lime'),           
        (6, 'grey'),         
        (7, 'lightgrey'),     
        (8, 'lightgreen')    
    ]

    colors = [color for value, color in custom_cmap if color != 'None']
    plt.switch_backend('agg')
    cmap = mcolors.ListedColormap(colors)
    data = masked.to_numpy().copy()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(data, cmap=cmap) 
    ax.axis('off')  

    return carbon_nlcd, fig