# http://code.google.com/p/python-weather-api/
# -*- coding: utf-8 -*-
import calendar
import os
import pywapi as weather
import sys
from console_size import get_terminal_size

# parameters:
metric = True
location = '80302'
sep = '/'
weekend_only = False
#
if metric:
	degree_unit="C"
else:
	degree_unit="F"
degree_unit_symbol="*"+degree_unit
#degree_unit_symbol="\xB0"+degree_unit

#
FtoC=lambda _: "%.0f" % ((float(_)-32.0)*5.0/9.0)
#
def get_current(google_result):
	"""
	Return a brief summary of current conditions from a pywapi google result.
	"""
	current=google_result['current_conditions']
	temp = current['temp_c'] if metric else current['temp_f']
	return temp + degree_unit_symbol + " and " + current['condition']
#
def get_forecast(google_result, forecast_number = 0, weekend_only = False):
	"""
	Return a forecast from a pywapi google result. forecast_number = 1 returns
	tomorrow's forecast. weekend_only returns a list with up to 3 elements.
	"""
	if weekend_only:
		forecasts = [ _ for _ in google_result['forecasts'] if _['day_of_week'].title() in calendar.day_abbr[-3:] ]
	else:
		forecasts=google_result['forecasts']
	try:
		forecast = forecasts[forecast_number]
	except IndexError:
		return ""
	if metric:
		low, high = FtoC(forecast['low']), FtoC(forecast['high'])
	else:
		low, high = forecast['low'], forecast['high']
	return forecast['day_of_week']+": "+low+"-"+high+degree_unit_symbol+" and "+forecast['condition']
#
rows, columns = get_terminal_size(default = (40, 80))
google_result = weather.get_weather_from_google(location)
#
this_line, last_line = "Now: "+get_current(google_result), "No weather"
forecast_number = 0
while len(this_line) < columns:
	last_line = this_line
	forecast = get_forecast(google_result, forecast_number=forecast_number, weekend_only=weekend_only)
	#
	if not forecast:
		break
	this_line = last_line+sep+forecast
	forecast_number += 1

print last_line