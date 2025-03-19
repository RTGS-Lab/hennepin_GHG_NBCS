from load import *
from processing import mlccs, esa, nlcd

def recursive_wrapper(data, initial_depth): #depth 0-7
	"""
	Creates all possible combinations of the given classes.

	Args:
		data (np.array): An array of class-groups, e.g. [[agro_1, agro_2, agro_3], [tree_1, tree_2, tree_3]...]
		initial_depth (boolean): The number of groups to include.
	Returns:
	    	D (dict): A dictionary of all the possible combinations.
	"""
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

def count_unique_dfs(dfs):
	"""
	Counts unique pandas dataframes to check if the combinating process was successfull.

	Args:
		dfs (dict): A dictionary of pandas dataframes.
	Returns:
	    	int: The number of the unique datasets.
	"""
	unique_dfs = set()
    
	for key, df in dfs.items():
		# Convert DataFrame to a tuple of tuples (hashable)
		df_tuple = tuple(map(tuple, df.to_numpy()))
		unique_dfs.add(df_tuple)
    
	return len(unique_dfs)
   
   
def lc_boostrapping(R, data, keys=None):
	"""
	Apply storage and sequestration rates to a certain land cover map.

	Args:
		R (dict): A dictionary of all the possible combinations.
		data (list/dict): A list or a dictionary with land cover pixel counts.
		keys (list): The names of the pixel classes. Defaults None.
	Returns:
	    	storages (list): A list of storage rates.
	    	seqs (list): A list of sequestration rates.
	"""
	
	from collections import Counter
	
	storages, seqs = [], []
	counted = Counter(data) if type(data)!=dict else dict(zip(keys,list(data.values())))
	for i in range(len(R)):
		df=R[i]
		st, sq = 0, 0
		for key in counted:
			if key!=None:
				st+=counted[key]*df[df.land_cover==key].storage.item()
				sq+=counted[key]*df[df.land_cover==key].sequestration.item()
		st /= sum(counted.values())
		sq /= sum(counted.values())
		storages.append(st)
		seqs.append(sq)
	
	return storages, seqs
	    
def nc_to_xr(path):
	"""
	Reads FLUXCOM nc files and wraps them into an xarray dataset.

	Args:
		path (str): The path to the files.
	Returns:
	    	xarray_dataset (xr.Dataset): The FLUXCOM dataset. 
	"""
	import netCDF4 as nc
	
	nc_dataset = nc.Dataset(path, mode='r')
	data_vars = {}
	coords = {}
	for var_name in nc_dataset.variables:
		var_data = nc_dataset.variables[var_name][:]
		if var_name in nc_dataset.dimensions:  
			coords[var_name] = var_data
		else:
			dims = nc_dataset.variables[var_name].dimensions
			data_vars[var_name] = (dims, var_data)
    
	attrs = nc_dataset.__dict__
    
	xarray_dataset = xr.Dataset(data_vars, coords=coords, attrs=attrs)
	return xarray_dataset
    	
#======================Boostrapping inventory data======================
for i in range(1,4):
    if 'df' not in globals():
        df = pd.read_csv(f'../data/Inventory_{i}.csv')
    else:
        df_new = pd.read_csv(f'../data/Inventory_{i}.csv')
        df = pd.concat([df, df_new]).reset_index(drop=True)
data=[]
for label, group in df.groupby('land_cover'):
    data.append(group)
    
R = recursive_wrapper(data, 7)
assert count_unique_dfs(R)==243 # Cheking if the number of bootstrapped combinations is correct

#======================Boostrapped x MLCCS======================
data = mlccs.MLCCS(shape, plot=True)
carbon = pd.DataFrame(columns=['storage', 'sequestration'])
carbon.storage, carbon.sequestration = lc_boostrapping(R, data)
carbon.to_csv('../data/mlccs_bootstrapped.csv', index=None)

#======================Boostrapped x NLCD======================
data = nlcd.NLCD(shape)
carbon = pd.DataFrame(columns=['storage', 'sequestration'])
carbon.storage, carbon.sequestration = lc_boostrapping(R, data)
carbon.to_csv('../data/nlcd_bootstrapped.csv', index=None)

#======================Boostrapped x ESA======================
data = esa.ESA(shape)
keys = ['Forest','Grassland', 'Agro', 'Urban', 'Sparsely vegetated', 'Wetland']
carbon = pd.DataFrame(columns=['storage', 'sequestration'])
carbon.storage, carbon.sequestration = lc_boostrapping(R, data, keys)
carbon.to_csv('../data/esa_bootstrapped.csv', index=None)

#======================FLUXCOM======================
xrs = []
files = [f for f in listdir('../data/fluxcom') if f!='FLUXCOM.nc']
for f in sorted(files):
    try:
        xrs.append(nc_to_xr('../data/fluxcom/'+f).mean('time')['NEE'].sel(lon=slice(-94 ,-93), lat=slice(45.3,44.7)))
    except OSError:
        pass
fluxcom = xr.concat(xrs, dim='time')
fluxcom['time'] = [x for x in range(2002,2021)]
fluxcom.to_netcdf('../data/FLUXCOM.nc')

#======================Landsat NPP======================
files = listdir('../data/LS_NPP')
npps = []
for f in sorted(files):
    
    data = np.load(f'../data/LS_NPP/{f}')

    data_array = xr.DataArray(
    data[0],
    coords={
        'latitude': (['latitude', 'longitude'], data[1]), 
        'longitude': (['latitude', 'longitude'], data[2])
    },
    dims=['latitude','longitude']
    )

    ds = xr.Dataset({'npp': data_array})
    npps.append(ds)
    
npp = xr.concat(npps, dim='time')
npp['time'] = [x for x in range(1986,2021)]
npp.to_netcdf('../data/LS_NPP.nc')

#======================MOD NPP======================
files = listdir('../data/MOD_NPP')
npps = []
for f in sorted(files):
    
    data = np.load(f'../data/MOD_NPP/{f}')

    data_array = xr.DataArray(
    data[0],
    coords={
        'latitude': (['latitude', 'longitude'], data[1]), 
        'longitude': (['latitude', 'longitude'], data[2])
    },
    dims=['latitude','longitude']
    )

    ds = xr.Dataset({'npp': data_array})
    npps.append(ds)  
npp = xr.concat(npps, dim='time')
npp['time'] = [x for x in range(2001,2020)]
npp.to_netcdf('../data/MOD_NPP.nc')


#======================MiCASA======================  
files = listdir('../data/MiCASA')
dates, micasa = [], []
for f in sorted(files):
    ds = rxr.open_rasterio(f'../data/MiCASA/{f}')
    ds = ds[1].sel(x=slice(-94 ,-93), y=slice(45.3,44.7))
    dates.append(ds['NEE'].time.values[0])
    micasa.append(ds['NEE'])

MiCASA = xr.concat(micasa, dim='time') 
MiCASA['time'] = pd.DatetimeIndex([date.strftime() for date in MiCASA.time.values])
MiCASA.to_netcdf('../data/micasa.nc')
