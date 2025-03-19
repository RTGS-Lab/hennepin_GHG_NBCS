import ee
import geemap
import json
import os
from collections import Counter
from shapely.geometry import Point

def ESA(shape, plot=True):
	"""
	Process ESA land cover map.

	Args:
		shape (geopandas.dataframe): Hennepin shape file to mask the data.
		plot (boolean): Plot or not.
	Returns:
	    	list: A list of pixels classified.
	"""
	#======================Deriving data from GEE======================
	ee.Authenticate()
	ee.Initialize(project='deepcarbon')
	
	js = json.loads(shape.to_json())
	roi = ee.Geometry(ee.FeatureCollection(js).geometry())

	dataset = ee.ImageCollection('ESA/WorldCover/v200')\
		    .filter(ee.Filter.eq('system:index', '2021'))\
		    .filterBounds(roi)\
		    .first()\
		    .select('Map')
		    
	pixel_counts = dataset.reduceRegion(
	reducer=ee.Reducer.frequencyHistogram(),
	    geometry=roi,
	    scale=10,  
	    maxPixels=1e20
	)
	esa_counts = pixel_counts.getInfo()['Map']
	del esa_counts['80'] # dropping water cells
	
	if plot:
		#======================Plotting the map of ESA for Hennepin======================
		output_dir = os.path.join(os.path.dirname(__file__), '../../results')
		poly = shape.geometry.unary_union

		m = geemap.Map()
		m.set_center(poly.centroid.x, poly.centroid.y, 12)
		#m.add_layer(roi, {'color':'white'}, 'NLCD')
		m.add_layer(dataset.clip(roi))
		#m.add_legend(builtin_legend="CGLS", title="CGLS Land Cover")
		m.save_map(os.path.join(output_dir,'ESA_map.html'))
		m.to_image(os.path.join(output_dir,'ESA_map.png'))
		
	return esa_counts
