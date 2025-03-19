import numpy as np
import geopandas as gpd
import xarray as xr
import regionmask
import rioxarray as rxr
from os import listdir

from meta import *
from bootstrapped import *
from northflux import *
from plot import *

import warnings

warnings.filterwarnings('ignore')

def load_data(name, path, shape):
	"""
	Loads and masks dataset.

	Args:
		name (str): Dataset name (northflux, ls, mod, micasa).
		path (str): Path to the dataset.
		shape (geopandas.dataframe): Hennepin shape file to mask the data.
	Returns:
	    	data (xarray.dataset): Masked dataset with converted carbon fluxes.
	"""
	if name in ['ls', 'mod']:
		variable = 'npp'
	elif name=='northflux':
		variable = 'nee'
	else:
		variable = 'NEE'
	
	raw = xr.open_dataset(path)
	shape['new_column'] = 0
	sv = shape.dissolve(by='new_column')['geometry']
	rg = regionmask.mask_3D_geopandas(sv, lon_or_obj=raw[lons[name]], lat=raw[lats[name]])
	data = raw[variable].where(rg) * units[name]
	return data
