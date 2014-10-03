#!/usr/local/bin/python

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import argparse
import sys
from matplotlib.dates import YearLocator

parser = argparse.ArgumentParser()
parser.add_argument("--veg", help="Veg type")
args = parser.parse_args()

########################### user defined #############################
nversion = 4

# vic output files
# [year] [month] [day] [hour] [precip (mm/ts)] [total ET (mm/ts)] [surface runoff (mm/ts)] [baseflow (mm/ts)] [air temperature (degC)] [soil liquid content 1 (mm)] [soil liquid content 2 (mm)] [soil liquid content 3 (mm)] [total swe (mm)] [canapy swe (mm)] [snow melt (mm/ts)] [snow fall (mm/ts)]
vic_output_path = []
vic_output_path.append('/raid2/ymao/VIC_versions_snow_comparison/vic_output/20140930/veg_%s/v4.0.6/fluxes_48.59375_-120.21875' %args.veg)
vic_output_path.append('/raid2/ymao/VIC_versions_snow_comparison/vic_output/20140930/veg_%s/v4.1.0.r4h/fluxes_48.59375_-120.21875' %args.veg)
vic_output_path.append('/raid2/ymao/VIC_versions_snow_comparison/vic_output/20140930/veg_%s/v4.1.1/fluxes_48.59375_-120.21875' %args.veg)
vic_output_path.append('/raid2/ymao/VIC_versions_snow_comparison/vic_output/20140930/veg_%s/v4.1.2.m/fluxes_48.59375_-120.21875' %args.veg)

# output plot file
result_dir = '/raid2/ymao/VIC_versions_snow_comparison/result_analysis/plot/20140930/energy_balance'

# version name
version = []
version.append("v4.0.6")
version.append("v4.1.0.r4h")
version.append("v4.1.1")
version.append("v4.1.2.m")

# model setting
balance = "Energy balance"

# time
skiprows = 0 # 201624
dtime = 1 # time step, hour
sim_start_time = dt.datetime(year=1987, month=1, day=1, hour=0) # simulation start time
sim_end_time = dt.datetime(year=2011, month=12, day=31, hour=23) # simulation start time
plot_start_time = dt.datetime(year=1993, month=1, day=1, hour=0) # plot start time
plot_end_time = dt.datetime(year=2011, month=12, day=31, hour=23) # plot end time
plot_year_interval = 1

duration = plot_end_time - plot_start_time
ntime = (duration.days*24 + duration.seconds//3600)/dtime+1
dates = []
for i in range(ntime):
	dates.append(plot_start_time + dt.timedelta(hours=i*dtime))

# variables
var_list = ['Precipitation', 'ET', 'Surface_runoff', 'Baseflow', 'Air_temperature', 'Soil_moisture_1', 'Soil_moisture_2', 'Soil_moisture_3', 'SWE', 'Canopy_snow', 'Snow_melt', 'Snow_fall'] # start from 5th column
units = {'Precipitation': 'mm/hr',
         'ET': 'mm/hr',
         'Surface_runoff': 'mm/hr',
         'Baseflow': 'mm/hr',
         'Air_temperature': 'degC',
         'Soil_moisture_1': 'mm',
         'Soil_moisture_2': 'mm',
         'Soil_moisture_3': 'mm',
         'SWE': 'mm',
         'Canopy_snow': 'mm',
         'Snow_melt': 'mm/hr',
         'Snow_fall': 'mm/hr',
} 
nvar = len(var_list)

########################### load data #############################
vic_output = []
for i in range(nversion):
	print "Loading data %d..." %(i+1)
	vic_output.append(np.loadtxt(vic_output_path[i], skiprows=skiprows))  

######################## plot time series #########################
# plot time series
for i in range(nvar):
	print "Plotting variable %d..." %(i+1)
	fig = plt.figure(figsize=(16,8))
	ax = plt.axes()
	start_lag = plot_start_time - sim_start_time
	start_ind = (start_lag.days*24 + start_lag.seconds//3600)/dtime
	end_lag = plot_end_time - sim_start_time
	end_ind = (end_lag.days*24 + end_lag.seconds//3600)/dtime
	color = ['m', 'r', 'g', 'b']
	for j in range(nversion):
		ax.plot_date(dates, vic_output[j][start_ind:end_ind+1,i+4], color[j], label=version[j])
	plt.xlim(plot_start_time, plot_end_time)
	years = YearLocator(plot_year_interval)
	ax.xaxis.set_major_locator(years)
	for tick in ax.xaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	plt.legend(loc=1, prop={'size':16})
	plt.ylabel('%s (%s)' %(var_list[i], units[var_list[i]]), fontsize=16)
	plt.title('%s, veg%s' %(balance, args.veg), fontsize=20)
	fig.savefig('%s/ts_%s_veg%s.png' %(result_dir, var_list[i], args.veg), format='png')

# plot version difference
for i in range(nvar):
	print "Plotting variable %d..." %(i+1)
	fig = plt.figure(figsize=(16,8))
	ax = plt.axes()
	start_lag = plot_start_time - sim_start_time
	start_ind = (start_lag.days*24 + start_lag.seconds//3600)/dtime
	end_lag = plot_end_time - sim_start_time
	end_ind = (end_lag.days*24 + end_lag.seconds//3600)/dtime
	color = ['m', 'r', 'g', 'b']
	for j in range(nversion-1):
		ax.plot_date(dates, vic_output[j+1][start_ind:end_ind+1,i+4]-vic_output[j][start_ind:end_ind+1,i+4], color[j+1], label='%s-%s' %(version[j+1], version[j]))
	plt.xlim(plot_start_time, plot_end_time)
	years = YearLocator(plot_year_interval)
	ax.xaxis.set_major_locator(years)
	for tick in ax.xaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	plt.legend(loc=1, prop={'size':16})
	plt.ylabel('%s (%s)' %(var_list[i], units[var_list[i]]), fontsize=16)
	plt.title('%s, veg%s' %(balance, args.veg), fontsize=20)
	fig.savefig('%s/ts_diff_%s_veg%s.png' %(result_dir, var_list[i], args.veg), format='png')


################# plot ground SWE (total SWE - canopy SWE) ################
# plot time series
fig = plt.figure(figsize=(16,8))
ax = plt.axes()
start_lag = plot_start_time - sim_start_time
start_ind = (start_lag.days*24 + start_lag.seconds//3600)/dtime
end_lag = plot_end_time - sim_start_time
end_ind = (end_lag.days*24 + end_lag.seconds//3600)/dtime
color = ['m', 'r', 'g', 'b']
for j in range(nversion):
	ax.plot_date(dates, vic_output[j][start_ind:end_ind+1,12]-vic_output[j][start_ind:end_ind+1,13], color[j], label=version[j])
plt.xlim(plot_start_time, plot_end_time)
years = YearLocator(plot_year_interval)
ax.xaxis.set_major_locator(years)
for tick in ax.xaxis.get_major_ticks():
	tick.label.set_fontsize(16)
for tick in ax.yaxis.get_major_ticks():
	tick.label.set_fontsize(16)
plt.legend(loc=1, prop={'size':16})
plt.ylabel('%s (%s)' %('Ground snow', 'mm'), fontsize=16)
	plt.title('%s, veg%s' %(balance, args.veg), fontsize=20)
fig.savefig('%s/ts_%s_veg%s.png' %(result_dir, 'Ground_snow', args.veg), format='png')
# plot version difference
fig = plt.figure(figsize=(16,8))
ax = plt.axes()
start_lag = plot_start_time - sim_start_time
start_ind = (start_lag.days*24 + start_lag.seconds//3600)/dtime
end_lag = plot_end_time - sim_start_time
end_ind = (end_lag.days*24 + end_lag.seconds//3600)/dtime
color = ['m', 'r', 'g', 'b']
for j in range(nversion-1):
	ax.plot_date(dates, (vic_output[j+1][start_ind:end_ind+1,12]-vic_output[j+1][start_ind:end_ind+1,13])-(vic_output[j][start_ind:end_ind+1,12]-vic_output[j][start_ind:end_ind+1,13]), color[j+1], label='%s-%s' %(version[j+1], version[j]))
plt.xlim(plot_start_time, plot_end_time)
years = YearLocator(plot_year_interval)
ax.xaxis.set_major_locator(years)
for tick in ax.xaxis.get_major_ticks():
	tick.label.set_fontsize(16)
for tick in ax.yaxis.get_major_ticks():
	tick.label.set_fontsize(16)
plt.legend(loc=1, prop={'size':16})
plt.ylabel('%s (%s)' %('Grownd snow', 'mm'), fontsize=16)
plt.title('%s, veg%s' %(balance, args.veg), fontsize=20)
fig.savefig('%s/ts_diff_%s_veg%s.png' %(result_dir, 'Ground_snow', args.veg), format='png')





