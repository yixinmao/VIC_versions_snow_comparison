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
vic_output_path.append('/raid2/ymao/VIC_versions_snow_comparison/vic_output/20141003_EnergyBalance/veg_%s/v4.0.6/fluxes_48.59375_-120.21875' %args.veg)
vic_output_path.append('/raid2/ymao/VIC_versions_snow_comparison/vic_output/20141003_EnergyBalance/veg_%s/v4.1.0.r4h/fluxes_48.59375_-120.21875' %args.veg)
vic_output_path.append('/raid2/ymao/VIC_versions_snow_comparison/vic_output/20141003_EnergyBalance/veg_%s/v4.1.1/fluxes_48.59375_-120.21875' %args.veg)
vic_output_path.append('/raid2/ymao/VIC_versions_snow_comparison/vic_output/20141003_EnergyBalance/veg_%s/v4.1.2.m/fluxes_48.59375_-120.21875' %args.veg)

# output plot file
result_dir = '/raid2/ymao/VIC_versions_snow_comparison/result_analysis/plot/20141003_EnergyBalance'

# version name
version = []
version.append("v4.0.6")
version.append("v4.1.0.r4h")
version.append("v4.1.1")
version.append("v4.1.2.m")

# model setting
balance = "Energy balance"

# time
#skiprows = 201624
skiprows = 0 # 201624
dtime = 1 # time step, hour
sim_start_time = dt.datetime(year=1987, month=1, day=1, hour=0) # simulation start time
#sim_start_time = dt.datetime(year=2010, month=1, day=1, hour=0) # simulation start time
sim_end_time = dt.datetime(year=2011, month=12, day=31, hour=23) # simulation start time
plot_start_time = dt.datetime(year=1993, month=1, day=1, hour=0) # plot start time
#plot_start_time = dt.datetime(year=2010, month=1, day=1, hour=0) # plot start time
plot_end_time = dt.datetime(year=2011, month=12, day=31, hour=23) # plot end time
plot_year_interval = 1
nyear = plot_end_time.year - plot_start_time.year

duration = plot_end_time - plot_start_time
ntime = (duration.days*24 + duration.seconds//3600)/dtime+1
dates = []
for i in range(ntime):
	dates.append(plot_start_time + dt.timedelta(hours=i*dtime))

# variables
var_list = ['Precipitation', 'ET', 'Surface_runoff', 'Baseflow', 'Air_temperature', 'Soil_moisture_1', 'Soil_moisture_2', 'Soil_moisture_3', 'SWE', 'Canopy_snow', 'Snow_melt', 'Snow_fall', 'Canopy_evap', 'Canopy_snow_sub', 'Snow_sub', 'Snow_surf_sub']
var_dict = {'Precipitation': [[4,4,4,4], 'mm/hr'], # column in each version (index starting from 0)
         'ET': [[5,5,5,5], 'mm/hr'],
         'Surface_runoff': [[6,6,6,6], 'mm/hr'],
         'Baseflow': [[7,7,7,7], 'mm/hr'],
         'Air_temperature': [[8,8,8,8], 'degC'],
         'Soil_moisture_1': [[9,9,9,9], 'mm'],
         'Soil_moisture_2': [[10,10,10,10], 'mm'],
         'Soil_moisture_3': [[11,11,11,11], 'mm'],
         'SWE': [[12,12,12,12], 'mm'],
         'Canopy_snow': [[13,13,13,13], 'mm'],
         'Snow_melt': [[14,14,14,14], 'mm/hr'],
         'Snow_fall': [[15,15,15,15], 'mm/hr'],
         'Canopy_evap': [[16,16,16,16], 'mm/hr'],
         'Canopy_snow_sub': [[17,17,17,17], 'mm/hr'],
         'Snow_sub': [[18,18,18,18], 'mm/hr'],
         'Snow_surf_sub': [[-1,19,19,19], 'mm/hr'], # -1 for no data for this var in this version
} 
nvar = len(var_list)

########################### load data #############################
vic_output = []
for i in range(nversion):
	print "Loading data %d..." %(i+1)
	vic_output.append(np.loadtxt(vic_output_path[i], skiprows=skiprows))  


################# plot daily average over all years (skip leap years) #################
# create a list of 365 days (starting from Oct 1)
dates_year_example = []
dates_year = {}
for i in range(365):
	date = dt.datetime(year=2010, month=10, day=1) + dt.timedelta(days=i)
	dates_year[date.month*100 + date.day] = i
	dates_year_example.append(date)

i = []

for var in var_list:
	print "Plotting variable %s..." %var
	# calculate daily average over all years (skip leap years)
	start_lag = plot_start_time - sim_start_time
	start_ind = (start_lag.days*24 + start_lag.seconds//3600)/dtime
	end_lag = plot_end_time - sim_start_time
	end_ind = (end_lag.days*24 + end_lag.seconds//3600)/dtime
	var_avg = np.zeros([nversion, 365])
	count = np.zeros([nversion, 365])
	for j in range(nversion):
		var_ind = var_dict[var][0][j]  # index of column of this var in this version
		if var_ind==-1: # if this var does not exist in this version
			continue
		for t in range(start_ind, end_ind+1):
			year = vic_output[j][t,0]
			mon = vic_output[j][t,1]
			day = vic_output[j][t,2]
			if year%4==0: # if leap year, skip
				continue
			day_ind = dates_year[mon*100+day]
			var_avg[j,day_ind] = var_avg[j,day_ind] + vic_output[j][t,var_ind]
			count[j,day_ind] = count[j,day_ind] + 1
		var_avg[j] = var_avg[j] / count[j]

	# plot time series
	fig = plt.figure(figsize=(16,8))
	ax = plt.axes()
	color = ['m', 'r', 'g', 'b']
	for j in range(nversion):
		var_ind = var_dict[var][0][j]  # index of column of this var in this version
		if var_ind==-1: # if this var does not exist in this version
			continue
		ax.plot_date(dates_year_example, var_avg[j], color[j], label=version[j])
	ax.xaxis.set_major_formatter(DateFormatter("%b"))
	for tick in ax.xaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	plt.legend(loc=1, prop={'size':16})
	plt.ylabel('%s (%s)' %(var, var_dict[var][1]), fontsize=16)
	plt.title('%s, veg%s' %(balance, args.veg), fontsize=20)
	fig.savefig('%s/ts_dailyAvg_%s_veg%s.png' %(result_dir, var, args.veg), format='png')

	# plot model difference
	fig = plt.figure(figsize=(16,8))
	ax = plt.axes()
	color = ['m', 'r', 'g', 'b']
	for j in range(nversion-1):
		var_ind = var_dict[var][0][j]  # index of column of this var in this version
		var_ind_next = var_dict[var][0][j+1]
		if var_ind==-1 or var_ind_next==-1: # if this var does not exist in this version
			continue
		ax.plot_date(dates_year_example, var_avg[j+1]-var_avg[j], color[j+1], label='%s-%s' %(version[j+1], version[j]))
	ax.xaxis.set_major_formatter(DateFormatter("%b"))
	for tick in ax.xaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(16)
	plt.legend(loc=1, prop={'size':16})
	plt.ylabel('%s (%s)' %(var, var_dict[var][1]), fontsize=16)
	plt.title('%s, veg%s' %(balance, args.veg), fontsize=20)
	fig.savefig('%s/ts_diff_dailyAvg_%s_veg%s.png' %(result_dir, var, args.veg), format='png')

	# plot accumlated time series
	if var_dict[var][1]=='mm/hr':  # if flux, plot and change unit to mm (NOTE: first convert to mm/day)
		fig = plt.figure(figsize=(16,8))
		ax = plt.axes()
		color = ['m', 'r', 'g', 'b']
		for j in range(nversion):
			var_ind = var_dict[var][0][j]  # index of column of this var in this version
			if var_ind==-1: # if this var does not exist in this version
				continue
			ax.plot_date(dates_year_example, np.cumsum(var_avg[j]*24), color[j], label=version[j])
		ax.xaxis.set_major_formatter(DateFormatter("%b"))
		for tick in ax.xaxis.get_major_ticks():
			tick.label.set_fontsize(16)
		for tick in ax.yaxis.get_major_ticks():
			tick.label.set_fontsize(16)
		plt.legend(loc=2, prop={'size':16})
		plt.ylabel('%s (%s)' %(var, 'mm'), fontsize=16)
		plt.title('Accumulated, %s, veg%s' %(balance, args.veg), fontsize=20)
		fig.savefig('%s/ts_accum_dailyAvg_%s_veg%s.png' %(result_dir, var, args.veg), format='png')

		# plot accumulated model difference
		fig = plt.figure(figsize=(16,8))
		ax = plt.axes()
		color = ['m', 'r', 'g', 'b']
		for j in range(nversion-1):
			var_ind = var_dict[var][0][j]  # index of column of this var in this version
			var_ind_next = var_dict[var][0][j+1]
			if var_ind==-1 or var_ind_next==-1: # if this var does not exist in this version
				continue
			ax.plot_date(dates_year_example, np.cumsum((var_avg[j+1]-var_avg[j])*24), color[j+1], label='%s-%s' %(version[j+1], version[j]))
		ax.xaxis.set_major_formatter(DateFormatter("%b"))
		for tick in ax.xaxis.get_major_ticks():
			tick.label.set_fontsize(16)
		for tick in ax.yaxis.get_major_ticks():
			tick.label.set_fontsize(16)
		plt.legend(loc=2, prop={'size':16})
		plt.ylabel('%s (%s)' %(var, 'mm'), fontsize=16)
		plt.title('Accumulated, %s, veg%s' %(balance, args.veg), fontsize=20)
		fig.savefig('%s/ts_diff_accum_dailyAvg_%s_veg%s.png' %(result_dir, var, args.veg), format='png')





