import xarray as xr
import regionmask

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from meta import units
	
def plot_northflux(data, shape, carbon, carbon_nlcd, carbon_esa):
	"""
	Plots and saves a map and time series of NEE over henneping county based on the NorthFlux estimation.

	Args:
		data (xarray.dataset): Masked dataset with converted carbon fluxes.
		shape (geopandas.dataframe): Hennepin shape file to mask the data.
		carbon (pandas.dataframe): NLCCS dataframe.
		carbon_nlcd (pandas.dataframe): NLCD dataframe.
		carbon_esa (pandas.dataframe): ESA dataframe.
	Returns:
	    	None
	"""
	fig, axd = plt.subplot_mosaic([['left', 'center', 'right'],
		                       ['buttom', 'buttom', 'buttom']],
		                      figsize=(16, 9), layout="constrained")
	d = {
	    'left':2020, 'center':2021, 'right':2021
	}
	for k, ax in axd.items():
	    if k!='buttom':
	    	if k!='right':
	    		data.sel(year = d[k]).plot(ax=ax,cmap='YlGn_r', vmin=-15, vmax=1, add_colorbar=False)
	    		ax.set_ylabel('')
    		else:
    			data.sel(year = d[k]).plot(ax=ax,cmap='YlGn_r', vmin=-15, vmax=1, cbar_kwargs={'shrink':0.6, 'label': "T CO₂e·ha\u207B\u00B9\u00A0yr\u207B\u00B9", 'orientation': 'vertical'})
    		if k == 'left':
    			ax.set_ylabel('Latitude, °')
    		shape.geometry.plot(ax=ax, facecolor="none", edgecolor='black')
    		ax.set_title(f'{d[k]}', fontsize=12)
    		ax.set_xlim(-94, -93)
    		ax.set_ylim(44.7 ,45.3)
    		ax.set_xlabel('Longitude, °')
	    else:
	    	data.mean(dim=['lat', 'lon']).plot(ax=ax, color='green', lw=3, label='NorthFlux')
	    	ax.axhline(carbon.sequestration.mean(), ls='--', color='grey', lw=2, label='MLCCS')
	    	ax.axhline(carbon_nlcd.sequestration.mean(), ls='--', color='orange', lw=2, label='NLCD')
	    	ax.axhline(carbon_esa.sequestration.mean(), ls='--', color='darkcyan', lw=2, label='ESA')
	    	ax.set_title(f'', fontsize=12)
	    	ax.set_ylabel(f'T CO₂e·ha\u207B\u00B9\u00A0yr\u207B\u00B9', fontsize=12)
	    	ax.set_xticks(ax.get_xticks().astype(int))
	    	ax.set_xlim(2020, 2022)
	    	plt.legend(loc='lower left')
	plt.title('Mean NorthFlux NEE: 2020-2022')
	plt.savefig(f'../results/NorthFlux.jpg')
	plt.show()
