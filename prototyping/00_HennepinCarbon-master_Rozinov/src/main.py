from load import *

#======================Hist plots from bootstrapped look up tables======================
boostrapped_plot(carbon, carbon_nlcd, carbon_esa)

#======================Box plots from bootstrapped look up tables======================
bootstrapped_boxplot(carbon, carbon_nlcd, carbon_esa)

#======================Loading and plotting NorthFlux dataset======================
north_flux = load_data('northflux', '../data/NorthFlux/NorthFlux_v01_nee_MEAN_2020-2022.nc', shape)
plot_northflux(north_flux, shape, carbon, carbon_nlcd, carbon_esa)

#======================Loading and plotting FLUXCOM dataset======================
fluxcom = xr.open_dataset('../data/fluxcom/FLUXCOM.nc').NEE 
fluxcom *= units['fluxcom']
plot(fluxcom, shape, carbon, carbon_nlcd, carbon_esa, 'fluxcom')

#======================Loading and plotting Landsat NPP dataset======================
ls = load_data('ls', '../data/LS_NPP.nc', shape)
plot(ls, shape, carbon, carbon_nlcd, carbon_esa, 'ls')

#======================Loading and plotting MOD NPP dataset======================
mod = load_data('mod', '../data/MOD_NPP.nc', shape)
plot(mod, shape, carbon, carbon_nlcd, carbon_esa, 'mod')

#======================Loading and plotting MiCASA NEE dataset======================
micasa = load_data('micasa', '../data/micasa.nc', shape).resample(time='Y').mean()
micasa["time"]=micasa["time"].dt.strftime("%Y").astype(int)

plot(micasa, shape, carbon, carbon_nlcd, carbon_esa, 'micasa')

#======================Plotting all the datasets together=====================
summary_plot(ls, mod, north_flux, fluxcom, micasa, metcouncil, carbon, carbon_nlcd, carbon_esa)

#======================Plotting all the datasets mean vs MetCouncil======================
summary_mean(ls, mod, north_flux, fluxcom, micasa, metcouncil, carbon, carbon_nlcd, carbon_esa)

#======================Plotting all the datasets mean vs MetCouncil vs Hennepin Goal======================
goal(ls, mod, north_flux, fluxcom, micasa, metcouncil, carbon, carbon_nlcd, carbon_esa, year=2050)
