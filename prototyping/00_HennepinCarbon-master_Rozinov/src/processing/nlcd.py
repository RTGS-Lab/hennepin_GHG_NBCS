import ee
import geemap
import json
import os
from collections import Counter
from shapely.geometry import Point

def NLCD(shape, plot=True):
	"""
	Process NLCD land cover map.

	Args:
		shape (geopandas.dataframe): Hennepin shape file to mask the data.
		plot (boolean): Plot or not.
	Returns:
	    	list: A list of pixels classified.
	"""
	#======================Deriving data from GEE======================
	ee.Authenticate()
	ee.Initialize()

	js = json.loads(shape.to_json())
	roi = ee.Geometry(ee.FeatureCollection(js).geometry())

	dataset = ee.ImageCollection('USGS/NLCD_RELEASES/2021_REL/NLCD')\
		    .filter(ee.Filter.eq('system:index', '2021'))\
		    .filterBounds(roi)\
		    .first()\
		    .select('landcover')
		    
	array = ee.data.computePixels({
			  'expression': dataset.clip(roi).select('landcover'),
			  'fileFormat': 'NUMPY_NDARRAY'
			})
	l =[]
	for i in range(len(array)): 
		for j in range(array.shape[1]):
			if array[i,j][0]!=0:
				l.append(array[i,j][0])
	
	#======================Reclustering the data======================
	classes = {
	    11: 'Open Water',
	    12: 'Perennial Ice/Snow',
	    21: 'Developed, Open Space',
	    22: 'Developed, Low Intensity',
	    23: 'Developed, Medium Intensity',
	    24: 'Developed, High Intensity',
	    31: 'Barren Land (Rock/Sand/Clay)',
	    41: 'Deciduous Forest',
	    42: 'Evergreen Forest',
	    43: 'Mixed Forest',
	    51: 'Dwarf Scrub',
	    52: 'Shrub/Scrub',
	    71: 'Grassland/Herbaceous',
	    72: 'Sedge/Herbaceous',
	    73: 'Lichens',
	    74: 'Moss',
	    81: 'Pasture/Hay',
	    82: 'Cultivated Crops',
	    90: 'Woody Wetlands',
	    95: 'Emergent Herbaceous Wetland',
	}
	NLCD_new_clusters = {
	    'Open Water': None,
	    'Perennial Ice/Snow': None, 
	    'Developed, Open Space': 'Sparsely vegetated',
	    'Developed, Low Intensity': 'Sparsely vegetated',
	    'Developed, Medium Intensity': 'Urban',
	    'Developed, High Intensity': 'Urban',
	    'Barren Land (Rock/Sand/Clay)': None,
	    'Deciduous Forest': 'Forest',
	    'Evergreen Forest': 'Forest',
	    'Mixed Forest': 'Forest',
	    'Dwarf Scrub': 'Shrub',
	    'Shrub/Scrub': 'Shrub',
	    'Grassland/Herbaceous': 'Grassland',
	    'Sedge/Herbaceous':'Grassland',
	    'Lichens': 'Heathland',
	    'Moss': 'Heathland',
	    'Pasture/Hay': 'Agro',
	    'Cultivated Crops': 'Agro', 
	    'Woody Wetlands': 'Wetland',
	    'Emergent Herbaceous Wetland': 'Wetland',
	}
	
	nlcd_pixels = []
	for i in range(len(l)):
		nlcd_pixels.append(NLCD_new_clusters[classes[l[i]]])
	if plot:
		#======================Plotting the map of NLCD for Hennepin======================
		output_dir = os.path.join(os.path.dirname(__file__), '../../results')
		poly = shape.geometry.unary_union

		m = geemap.Map()
		m.set_center(poly.centroid.x, poly.centroid.y, 12)
		#m.add_layer(roi, {'color':'white'}, 'NLCD')
		m.add_layer(dataset.clip(roi))
		#m.add_legend(builtin_legend="CGLS", title="CGLS Land Cover")
		m.save_map(os.path.join(output_dir,'NLCD_map.png'))
		m.to_image(os.path.join(output_dir,'NLCD_map.png'))
		
	return nlcd_pixels
	
