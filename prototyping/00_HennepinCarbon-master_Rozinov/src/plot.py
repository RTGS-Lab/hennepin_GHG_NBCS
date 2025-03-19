from meta import *

import pandas as pd
import geopandas as gpd
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

def plot(data, shape, carbon, carbon_nlcd, carbon_esa, name):
	"""
	Plots and saves a map and time series of carbon flux over henneping county based on the provided dataset.

	Args:
		data (xarray.dataset): Masked dataset with converted carbon fluxes.
		shape (geopandas.dataframe): Hennepin shape file to mask the data.
		carbon (pandas.dataframe): NLCCS dataframe.
		carbon_nlcd (pandas.dataframe): NLCD dataframe.
		carbon_esa (pandas.dataframe): ESA dataframe.
	Returns:
	    	None
	"""
	proj = ccrs.PlateCarree()

	fig = plt.figure(figsize=(14, 9))
	gs = fig.add_gridspec(1,2)
	ax1 = fig.add_subplot(gs[0, 0], projection=proj)
	ax2 = fig.add_subplot(gs[0, 1],)

	ax1.gridlines(draw_labels=True)
	data.mean('time').plot(ax=ax1,  cmap='YlGn_r', cbar_kwargs={'shrink':0.3,'label': "T CO₂e·ha\u207B\u00B9\u00A0yr\u207B\u00B9",
		                                                             'orientation': 'horizontal'})
	shape.plot(ax=ax1, color='None', edgecolor='black')
	ax1.set_title(titles[name])

	data.mean(dim=[lats[name], lons[name]]).plot(ax=ax2, color='green', lw=3, label=labels[name])
	ax2.axhline(carbon.sequestration.mean(), ls='--', color='grey', lw=2, label='MLCCS')
	ax2.axhline(carbon_nlcd.sequestration.mean(), ls='--', color='orange', lw=2, label='NLCD')
	ax2.axhline(carbon_esa.sequestration.mean(), ls='--', color='darkcyan', lw=2, label='ESA')
	ax2.set_title(f'', fontsize=12)
	ax2.set_ylabel(f'T CO₂e·ha\u207B\u00B9\u00A0yr\u207B\u00B9', fontsize=12)
	ax2.set_xticks(ax2.get_xticks().astype(int))
	ax2.set_xlabel('Year', fontsize=12)
	plt.legend(loc='lower left')
	plt.tight_layout()
	plt.savefig(f'../results/{name}.png')
	plt.show()

def summary_plot(ls, mod, northflux, fluxcom, micasa, metcouncil, carbon, carbon_nlcd, carbon_esa):
	"""
	Plots and saves a time series summary.

	Args:
		ls (xarray.dataset): Masked dataset with converted carbon fluxes.
		mod (xarray.dataset): Masked dataset with converted carbon fluxes.
		northflux (xarray.dataset): Masked dataset with converted carbon fluxes.
		fluxcom (xarray.dataset): Masked dataset with converted carbon fluxes.
		micasa (xarray.dataset): Masked dataset with converted carbon fluxes.
		metcouncil (float): MetCouncil 2021 estimation for Hennepin.
		carbon (pandas.dataframe): NLCCS dataframe.
		carbon_nlcd (pandas.dataframe): NLCD dataframe.
		carbon_esa (pandas.dataframe): ESA dataframe.
	Returns:
	    	None
	"""
	fig, ax = plt.subplots(figsize=(12,6))

	ls.mean(dim=['latitude', 'longitude']).plot(ax=ax, color='darkgreen', lw=2, label='Landsat NPP')
	mod.mean(dim=['latitude', 'longitude']).plot(ax=ax, color='indigo', lw=2, label='MOD NPP')
	northflux.mean(dim=['lat', 'lon']).plot(ax=ax, color='lightseagreen', lw=2, label='NorthFlux NEE')
	fluxcom.mean(dim=['lat', 'lon']).plot(ax=ax, color='darkslategrey', lw=2, label='FLUXCOM NEE')
	micasa.mean(dim=['y', 'x']).plot(color='lime', lw=2, label='MiCASA NEE')

	ax.axhline(carbon.sequestration.mean(), ls='--', color='grey', lw=2, label='MLCCS')
	ax.axhline(carbon_nlcd.sequestration.mean(), ls='--', color='orange', lw=2, label='NLCD')
	ax.axhline(carbon_esa.sequestration.mean(), ls='--', color='darkcyan', lw=2, label='ESA')
	ax.plot(2021, metcouncil, '-ro', markersize=10, label='MetCouncil Estimation')
	ax.axhline(metcouncil, color='red', lw=2)
	ax.spines[['right', 'top']].set_visible(False)

	plt.title('Model Comparison')
	plt.ylabel('T CO₂e·ha\u207B\u00B9\u00A0yr\u207B\u00B9')
	plt.legend(loc='lower left')
	plt.tight_layout()
	plt.savefig('../results/summary.png')
	plt.show()
	
def summary_mean(ls, mod, northflux, fluxcom, micasa, metcouncil, carbon, carbon_nlcd, carbon_esa):
	"""
	Plots and saves a time series summary with mean and std.

	Args:
		ls (xarray.dataset): Masked dataset with converted carbon fluxes.
		mod (xarray.dataset): Masked dataset with converted carbon fluxes.
		northflux (xarray.dataset): Masked dataset with converted carbon fluxes.
		fluxcom (xarray.dataset): Masked dataset with converted carbon fluxes.
		micasa (xarray.dataset): Masked dataset with converted carbon fluxes.
		metcouncil (float): MetCouncil 2021 estimation for Hennepin.
		carbon (pandas.dataframe): NLCCS dataframe.
		carbon_nlcd (pandas.dataframe): NLCD dataframe.
		carbon_esa (pandas.dataframe): ESA dataframe.
	Returns:
	    	None
	"""
	LS = pd.DataFrame({'year': ls.mean(dim=['latitude', 'longitude'])['time'].values.tolist(), 
                   'LS':ls.mean(dim=['latitude', 'longitude']).values.flatten()}).set_index('year')
	MOD = pd.DataFrame({'year': mod.mean(dim=['latitude', 'longitude'])['time'].values.tolist(), 
		            'MOD':mod.mean(dim=['latitude', 'longitude']).values.flatten()}).set_index('year')
	fc = pd.DataFrame({'year': fluxcom.mean(dim=['lat', 'lon'])['time'].values.tolist(), 
		                'fluxcom':fluxcom.mean(dim=['lat', 'lon']).values.flatten()}).set_index('year')
	nf = pd.DataFrame({'year': northflux.mean(dim=['lat', 'lon'])['year'].values.tolist(), 
		                'nf':northflux.mean(dim=['lat', 'lon']).values.flatten()}).set_index('year')
	MIC = pd.DataFrame({'year': micasa.mean(dim=['y', 'x'])['time'].values.tolist(), 
		                'MIC':micasa.mean(dim=['y', 'x']).values.flatten()}).set_index('year')
	df = pd.concat([LS, MOD, fc, nf, MIC], axis=1)
	df['MLCCS'] = [carbon.sequestration.mean()]*len(df)
	df['NLCD'] = [carbon_nlcd.sequestration.mean()]*len(df)
	df['ESA'] = [carbon_esa.sequestration.mean()]*len(df)
	df['std'] = df.std(axis=1)
	df['mean'] = df.drop('std', axis=1).mean(axis=1)
	
	fig, ax = plt.subplots(figsize=(12,6))

	ls.mean(dim=['latitude', 'longitude']).plot(ax=ax, color='grey', lw=0.5)
	northflux.mean(dim=['lat', 'lon']).plot(ax=ax, color='grey', lw=0.5)
	fluxcom.mean(dim=['lat', 'lon']).plot(ax=ax, color='grey', lw=0.5)
	micasa.mean(dim=['y', 'x']).plot(color='grey', lw=0.5)
	mod.mean(dim=['latitude', 'longitude']).plot(ax=ax, color='grey', lw=0.5)
	
	df['mean'].plot(ax=ax, color = 'darkgreen', lw=3.5, label='mean')
	ax.fill_between(df.index, df['mean']-df['std'], df['mean']+df['std'], color='lightgreen', alpha=0.4, label='std')

	ax.axhline(carbon.sequestration.mean(), color='grey', lw=0.5)
	ax.axhline(carbon_nlcd.sequestration.mean(), color='grey', lw=0.5)
	ax.axhline(carbon_esa.sequestration.mean(),  color='grey', lw=0.5)
	ax.plot(2021, metcouncil, marker='o', linestyle='-', color='maroon', markersize=5, label='MetCouncil Estimation')
	#ax.plot([2033,2050], [goal2033, goal2050], marker='o', linestyle='-', color='red', markersize=5, label='MetCouncil Goal')
	ax.axhline(metcouncil, color='maroon', lw=2)
	ax.spines[['right', 'top']].set_visible(False)
	#ax.set_ylim(-10,5)

	plt.title('Model Comparison')
	plt.ylabel('T CO₂e·ha\u207B\u00B9\u00A0yr\u207B\u00B9')
	plt.legend(loc='lower left')
	plt.tight_layout()
	plt.savefig('../results/summary_mean.png')
	plt.show()
	
def goal(ls, mod, northflux, fluxcom, micasa, metcouncil, carbon, carbon_nlcd, carbon_esa, year=2033):
	"""
	Plots and saves a time series summary with mean and std with Hennepin Climate Action Goals.

	Args:
		ls (xarray.dataset): Masked dataset with converted carbon fluxes.
		mod (xarray.dataset): Masked dataset with converted carbon fluxes.
		northflux (xarray.dataset): Masked dataset with converted carbon fluxes.
		fluxcom (xarray.dataset): Masked dataset with converted carbon fluxes.
		micasa (xarray.dataset): Masked dataset with converted carbon fluxes.
		metcouncil (float): MetCouncil 2021 estimation for Hennepin.
		carbon (pandas.dataframe): NLCCS dataframe.
		carbon_nlcd (pandas.dataframe): NLCD dataframe.
		carbon_esa (pandas.dataframe): ESA dataframe.
		year (int) (optional): Year of the goal 2033 or 2050.
	Returns:
	    	None
	"""
	LS = pd.DataFrame({'year': ls.mean(dim=['latitude', 'longitude'])['time'].values.tolist(), 
                   'LS':ls.mean(dim=['latitude', 'longitude']).values.flatten()}).set_index('year')
	MOD = pd.DataFrame({'year': mod.mean(dim=['latitude', 'longitude'])['time'].values.tolist(), 
		            'MOD':mod.mean(dim=['latitude', 'longitude']).values.flatten()}).set_index('year')
	fc = pd.DataFrame({'year': fluxcom.mean(dim=['lat', 'lon'])['time'].values.tolist(), 
		                'fluxcom':fluxcom.mean(dim=['lat', 'lon']).values.flatten()}).set_index('year')
	nf = pd.DataFrame({'year': northflux.mean(dim=['lat', 'lon'])['year'].values.tolist(), 
		                'nf':northflux.mean(dim=['lat', 'lon']).values.flatten()}).set_index('year')
	MIC = pd.DataFrame({'year': micasa.mean(dim=['y', 'x'])['time'].values.tolist(), 
		                'MIC':micasa.mean(dim=['y', 'x']).values.flatten()}).set_index('year')
	df = pd.concat([LS, MOD, fc, nf, MIC], axis=1)
	df['MLCCS'] = [carbon.sequestration.mean()]*len(df)
	df['NLCD'] = [carbon_nlcd.sequestration.mean()]*len(df)
	df['ESA'] = [carbon_esa.sequestration.mean()]*len(df)
	df['std'] = df.std(axis=1)
	df['mean'] = df.drop('std', axis=1).mean(axis=1)
	
	fig, ax = plt.subplots(figsize=(12,6))

	ls.mean(dim=['latitude', 'longitude']).plot(ax=ax, color='grey', lw=0.5)
	northflux.mean(dim=['lat', 'lon']).plot(ax=ax, color='grey', lw=0.5)
	fluxcom.mean(dim=['lat', 'lon']).plot(ax=ax, color='grey', lw=0.5)
	micasa.mean(dim=['y', 'x']).plot(color='grey', lw=0.5)
	mod.mean(dim=['latitude', 'longitude']).plot(ax=ax, color='grey', lw=0.5)
	
	df['mean'].plot(ax=ax, color = 'darkgreen', lw=3.5, label='mean')
	ax.fill_between(df.index, df['mean']-df['std'], df['mean']+df['std'], color='lightgreen', alpha=0.4, label='std')

	ax.axhline(carbon.sequestration.mean(), color='grey', lw=0.5)
	ax.axhline(carbon_nlcd.sequestration.mean(), color='grey', lw=0.5)
	ax.axhline(carbon_esa.sequestration.mean(),  color='grey', lw=0.5)
	ax.plot(2021, metcouncil, marker='o', linestyle='-', color='maroon', markersize=5, label='MetCouncil Estimation')
	if year==2033:	
		ax.plot([2033], [goal33], marker='o', linestyle='-', color='red', markersize=7, label='Hennepin Goal')
	else:
		ax.plot([2033, 2050], [goal33, goal50], marker='o', linestyle='-', color='red', markersize=7, label='Hennepin Goal')
	ax.axhline(metcouncil, color='maroon', lw=2)
	ax.spines[['right', 'top']].set_visible(False)
	#ax.set_ylim(-10,5)

	plt.title('Model Comparison')
	plt.ylabel('Metric tons CO2e·ha\u207B\u00B9 y\u207B\u00B9')
	plt.legend(loc='lower left')
	plt.tight_layout()
	plt.savefig(f'../results/summary_goal_{year}.png')
	plt.show()
