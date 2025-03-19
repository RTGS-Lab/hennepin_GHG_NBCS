import geopandas as gpd

#======================Loading Henneping boundaries======================
shape = gpd.read_file('../data/shp_bdry_census2020counties_ctus/Census2020Counties.shp').to_crs(4326)
shape = shape[shape['CO_NAME_FU']=='Hennepin County']

#======================Unit conversion coefficients======================
units = {
	'nlccs': 44 / 12 * (-1), # MgC ha-1 yr-1 -> Mg CO2e ha-1 yr-1 (or T CO2e ha-1 yr-1)
	'nlcd': 44 / 12 * (-1), # MgC ha-1 yr-1 -> Mg CO2e ha-1 yr-1 (or T CO2e ha-1 yr-1)
	'esa': 44 / 12 * (-1), # MgC ha-1 yr-1 -> Mg CO2e ha-1 yr-1 (or T CO2e ha-1 yr-1)
	'northflux': 44 / 12 * 10e-6 / 10e-4 * 365, # gC m-2 d-1 -> Mg CO2e ha-1 yr-1 (T CO2e ha-1 yr-1)
	'fluxcom': 44 /12 * 10e-6 / 10e-4 * 365, # gC m-2 d-1 -> Mg CO2e ha-1 yr-1 (T CO2e ha-1 yr-1)
	'ls': 0.0001*(-44 / 12 * 10e-3 / 10e-4), # scale_factor*unit_conversion: kgC m-2 yr-1 -> Mg CO2e ha-1 yr-1 (T CO2e ha-1 yr-1)
	'mod': 0.0001*(-44 / 12 * 10e-3 / 10e-4), # scale_factor*unit_conversion: kgC m-2 yr-1 -> Mg CO2e ha-1 yr-1 (T CO2e ha-1 yr-1)
	'micasa': 44 / 12 * 10e-3 / 10e-4 * (365 * 24 * 60 * 60), # kgC m-2 s-1 -> Mg CO2e ha-1 yr-1 (T CO2e ha-1 yr-1) 
	'cmip6': 44 / 12 * 10e-3 / 10e-4 * (365 * 24 * 60 * 60), # kgC m-2 s-1 -> Mg CO2e ha-1 yr-1 (T CO2e ha-1 yr-1)
	'met2021': 1e6 / 156810, # million Mg CO2e yr-1 -> Mg CO2e ha-1 yr-1
	'goal33': 1e6 / 156810, # million Mg CO2e yr-1 -> Mg CO2e ha-1 yr-1
	'goal50': 1e6 / 156810, # million Mg CO2e yr-1 -> Mg CO2e ha-1 yr-1
}

#======================MetCouncil Sequestration rates======================
seq = -0.34 
metcouncil = seq * units['met2021'] 

seq33 = -0.25
seq50 = -2.5

goal33 = seq33 * units['goal33']  
goal50 = seq50 * units['goal50'] 

#======================Plot meta info======================
titles = {
	'ls': 'Mean Landsat NPP: 1986-2020',
	'mod': 'Mean MODIS NPP: 2001-2019',
	'micasa': 'Mean MiCASA NEE: 2001-2023',
	'fluxcom': 'Mean FLUXCOM NEE: 2002-2020',
}

labels = {
	'ls': 'Landsat NPP',
	'mod': 'MOD NPP',
	'micasa': 'MiCASA NEE',
	'fluxcom': 'FLUXCOM NEE',
}

lats = {
		'ls': 'latitude',
		'fluxcom': 'lat',
		'mod': 'latitude',
		'northflux': 'lat',
		'micasa': 'y',
	}
lons = {
	'ls': 'longitude',
	'fluxcom': 'lon',
	'mod': 'longitude',
	'northflux': 'lon',
	'micasa': 'x',
}
