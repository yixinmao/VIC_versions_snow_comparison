#!/usr/local/bin/python

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import argparse
import sys
from matplotlib.dates import YearLocator, DateFormatter, MonthLocator

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
#sim_start_time = dt.datetime(year=2010, month=1, day=1, hour=0) # simulation start time
sim_end_time = dt.datetime(year=2011, month=12, day=31, hour=23) # simulation start time
plot_start_time = dt.datetime(year=1993, month=1, day=1, hour=0) # plot start time
#plot_start_time = dt.datetime(year=2011, month=1, day=1, hour=0) # plot start time
plot_end_time = dt.datetime(year=2011, month=12, day=31, hour=23) # plot end time
plot_year_interval = 1
nyear = plot_end_time.year - plot_start_time.year

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


################# plot daily average over all years (skip leap years) #################
# create a list of 365 days
dates_year_example = []
dates_year = {}
for i in range(365):
	date = dt.datetime(year=2011, month=1, day=1) + dt.timedelta(days=i)
	dates_year[date.month*100 + date.day] = i
	dates_year_example.append(date)
print len(dates_year)

for i in range(nvar):
	print "Plotting variable %d..." %(i+1)
	# calculate daily average over all years (skip leap years)
	start_lag = plot_start_time - sim_start_time
	start_ind = (start_lag.days*24 + start_lag.seconds//3600)/dtime
	end_lag = plot_end_time - sim_start_time
	end_ind = (end_lag.days*24 + end_lag.seconds//3600)/dtime
	var_avg = np.zeros([nversion, 365])
	count = np.zeros([nversion, 365])
	for j in range(nversion):
		for t in range(start_ind, end_ind+1):
			year = vic_output[j][t,0]
			mon = vic_output[j][t,1]
			day = vic_output[j][t,2]
			if year%4==0: # if leap year, skip
				continue
			day_ind = dates_year[mon*100+day]
			var_avg[j,day_ind] = var_avg[j,day_ind] + vic_output[j][t,i+4]
			count[j,day_ind] = count[j,day_ind] + 1
		var_avg[j] = var_avg[j] / count[j]

	# plot time series
	fig = plt.figure(figsize=(16,8))
	ax = plt.axes()
	color = ['m', 'r', 'g', 'b']
#	dates_year_example = dates_year_example[274:] + dates_year_example[:274]
	for j in range(nversion):
#		var_avg[j] = np.concatenate([var_avg[j,274:], var_avg[j,:274]])
		ax.plot_date(dates_year_example, var_avg[j], color[j], label=version[j])
#	months = MonthLocator([10,11,12,1,2,3,4,5,6,7,8,9])
#	ax.xaxis.set_major_locator(months)
	ax.xaxis.set_major_formatter(DateFormatter("%b"))
	for tick in ax.xaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	plt.legend(loc=1, prop={'size':16})
	plt.ylabel('%s (%s)' %(var_list[i], units[var_list[i]]), fontsize=16)
	plt.title('%s, veg%s' %(balance, args.veg), fontsize=20)
	fig.savefig('%s/ts_dailyAvg_%s_veg%s.png' %(result_dir, var_list[i], args.veg), format='png')

	# plot model difference
	fig = plt.figure(figsize=(16,8))
	ax = plt.axes()
	color = ['m', 'r', 'g', 'b']
#	dates_year_example = dates_year_example[274:] + dates_year_example[:274]
	for j in range(nversion-1):
#		var_avg[j] = np.concatenate([var_avg[j,274:], var_avg[j,:274]])
		ax.plot_date(dates_year_example, var_avg[j+1]-var_avg[j], color[j+1], label='%s-%s' %(version[j+1], version[j]))
#	months = MonthLocator([10,11,12,1,2,3,4,5,6,7,8,9])
#	ax.xaxis.set_major_locator(months)
	ax.xaxis.set_major_formatter(DateFormatter("%b"))
	for tick in ax.xaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	plt.legend(loc=1, prop={'size':16})
	plt.ylabel('%s (%s)' %(var_list[i], units[var_list[i]]), fontsize=16)
	plt.title('%s, veg%s' %(balance, args.veg), fontsize=20)
	fig.savefig('%s/ts_diff_dailyAvg_%s_veg%s.png' %(result_dir, var_list[i], args.veg), format='png')

