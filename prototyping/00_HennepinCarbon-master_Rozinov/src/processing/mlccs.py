import geopandas as gpd
import matplotlib.pyplot as plt
import os

def MLCCS(shape, plot=True):
	"""
	Process MLCCS land cover map.

	Args:
		shape (geopandas.dataframe): Hennepin shape file to mask the data.
		plot (boolean): Plot or not.
	Returns:
	    	list: A list of pixels classified.
	"""
	#======================Importing MLCCS======================
	lc = gpd.read_file('../data/shp_biota_landcover_mlccs/landcover_minnesota_land_cover_classification_system.shp').to_crs(4326)
	hennepin = gpd.clip(lc, shape[shape['CO_NAME_FU']=='Hennepin County']).reset_index(drop=True)

	#======================Reclustering the data======================
	classes = dict(zip([0, 11,12,13,14,15,21,22,23,24,31,32,51,52,61,62,63,71,81,82,90,92], 
		['Not Classified','5-10% Impervious', '11-25% Impervious', '26-50% Impervious', 
		'51-75% Impervious', '76-100% Impervious', 'Short Grasses', 'Agricultural Land',
		'Maintained Tall Grass', 'Tree Plantation', 'Forest', 'Wetland Forest', 'Shrubland',
		'Wetland Shrubs', 'Tall Grasses', 'Wetland Emergent Veg.', 'Dry Tall Grasses',  'Lichen Scrubland',
		'Rock Outcrop', 'Mud Flat','Open Water', 'Wetland Open Water',
		]))
	    
	new_clusters = {
	    'Not Classified': None,
	    '5-10% Impervious': 'Sparsely vegetated',
	    '11-25% Impervious': 'Sparsely vegetated',
	    '26-50% Impervious': 'Urban',
	    '51-75% Impervious': 'Urban',
	    '76-100% Impervious': 'Urban',
	    'Short Grasses': 'Heathland',
	    'Agricultural Land': 'Agro',
	    'Maintained Tall Grass': 'Grassland',
	    'Tree Plantation': 'Forest',
	    'Forest': 'Forest',
	    'Wetland Forest': 'Wetland',
	    'Shrubland': 'Shrub',
	    'Wetland Shrubs': 'Shrub',
	    'Tall Grasses': 'Grassland',
	    'Wetland Emergent Veg.': 'Wetland',
	    'Dry Tall Grasses': 'Grassland',
	    'Lichen Scrubland':'Tundra',
	    'Rock Outcrop': None,
	    'Mud Flat': 'Wetland',
	    'Open Water': None,
	    'Wetland Open Water': None
	}
	for idx, row in enumerate(hennepin.CARTO.values):
	    hennepin.loc[idx, 'CARTO'] = new_clusters[classes[hennepin.loc[idx, 'CARTO']]]
	    
	if plot:
		#======================Plotting the map of MLCCS for Hennepin======================
		output_dir = os.path.join(os.path.dirname(__file__), '../../results')
		fig, ax = plt.subplots(figsize=(16,9))
		shape.plot(color='white', edgecolor='black', ax=ax)
		hennepin.plot(column='CARTO', ax=ax, legend=True, cmap='tab10')
		plt.title('MLCCS', fontsize=16)
		plt.tight_layout()
		plt.savefig(os.path.join(output_dir,'MLCCS_map.png'))
		
	return hennepin.CARTO.tolist()
