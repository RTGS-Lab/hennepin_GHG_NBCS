import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt

from meta import units

#======================Loading Boostrapped Sequestration Rates======================
carbon = pd.read_csv('../data/mlccs_bootstrapped.csv')
carbon_nlcd = pd.read_csv('../data/nlcd_bootstrapped.csv')
carbon_esa = pd.read_csv('../data/esa_bootstrapped.csv')

carbon['sequestration'] *= units['nlccs']
carbon['storage'] *= -units['nlcd']
carbon_nlcd['sequestration'] *= units['nlcd']
carbon_nlcd['storage'] *= -units['nlcd']
carbon_esa['sequestration'] *= units['esa']
carbon_esa['storage'] *= -units['esa']


def boostrapped_plot(carbon, carbon_nlcd, carbon_esa):
	"""
	Plots and saves bootstrapped storage and sequestration rates histplots for different land cover maps.

	Args:
		carbon (pandas.dataframe): NLCCS dataframe.
		carbon_nlcd (pandas.dataframe): NLCD dataframe.
		carbon_esa (pandas.dataframe): ESA dataframe.
	Returns:
	    	None
	"""

	custom_params = {"axes.spines.right": False, "axes.spines.top": False}
	sns.set_theme(style="ticks", rc=custom_params)

	fig, ax = plt.subplots(3,2, figsize=(12,12))
	
	sns.histplot(data=carbon, x="storage", kde=True, ax=ax[0][0], color='darkgreen')
	sns.histplot(data=carbon, x="sequestration", kde=True, ax=ax[0][1], color='darkgreen')
	
	ax[0][0].set_ylabel("MLCCS Classification", fontsize=16)
	ax[0][1].set_ylabel("", fontsize=16)
	ax[0][0].set_title('Storage', fontsize=18)
	ax[0][1].set_title('Sequestration', fontsize=18)
	ax[0][0].set_xlabel('')
	ax[0][1].set_xlabel('')
	ax[0][0].set_xlim(145,500)
	ax[0][1].set_xlim(-30, -2)

	sns.histplot(data=carbon_nlcd, x="storage", kde=True, ax=ax[1][0], color='darkgreen')
	sns.histplot(data=carbon_nlcd, x="sequestration", kde=True, ax=ax[1][1], color='darkgreen')
	ax[1][0].set_ylabel("NLCD Classification", fontsize=16)
	ax[1][1].set_ylabel("", fontsize=16)
	ax[1][0].set_xlim(145,500)
	ax[1][1].set_xlim(-30, -2)

	sns.histplot(data=carbon_esa, x="storage", kde=True, ax=ax[2][0], color='darkgreen')
	sns.histplot(data=carbon_esa, x="sequestration", kde=True, ax=ax[2][1], color='darkgreen')
	ax[2][0].set_ylabel("ESA Classification", fontsize=16)
	ax[2][1].set_ylabel("", fontsize=16)
	ax[2][0].set_xlabel('T CO2e ha-1')
	ax[2][1].set_xlabel('T CO2e ha-1 yr-1')
	ax[2][0].set_xlim(145,500)
	ax[2][1].set_xlim(-30, -2)
	ax[2][0].set_xlabel('T CO2e ha-1')
	ax[2][1].set_xlabel('T CO2e ha-1 yr-1')
	
	plt.tight_layout()
	plt.savefig('../results/dists.png')
	plt.show()
	
def bootstrapped_boxplot(carbon, carbon_nlcd, carbon_esa):
	"""
	Plots and saves bootstrapped storage and sequestration rates boxplots for different land cover maps.

	Args:
		carbon (pandas.dataframe): NLCCS dataframe.
		carbon_nlcd (pandas.dataframe): NLCD dataframe.
		carbon_esa (pandas.dataframe): ESA dataframe.
	Returns:
	    	None
	"""
	stor_box = pd.concat([carbon.sequestration, carbon_nlcd.sequestration, carbon_esa.sequestration], axis=1)
	stor_box.columns = ['MLCCS', 'NLCD', 'ESA']
	stor_box = pd.melt(stor_box, var_name='Class', value_name='Seq')

	seq_box = pd.concat([carbon.storage, carbon_nlcd.storage, carbon_esa.storage], axis=1)
	seq_box.columns = ['MLCCS', 'NLCD', 'ESA']
	seq_box = pd.melt(seq_box, var_name='Class', value_name='Storage')
	
	custom_params = {"axes.spines.right": False, "axes.spines.top": False}
	sns.set_theme(style="ticks", rc=custom_params)

	fig, ax = plt.subplots(1,2, figsize=(16,9))
	sns.boxplot(x='Class', y='Storage', data=seq_box, ax=ax[0],color='darkgreen')
	sns.boxplot(x='Class', y='Seq', data=stor_box, ax=ax[1],color='darkgreen')

	ax[0].set_xlabel('Class')
	ax[1].set_xlabel('Class')
	ax[0].set_ylabel('T CO2e ha-1')
	ax[1].set_ylabel('T CO2e ha-1 yr-1')
	ax[0].set_title('Storage', fontsize=18)
	ax[1].set_title('Sequestration', fontsize=18)

	plt.savefig('../results/boxplot.png')
	plt.show()

