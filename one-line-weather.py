# http://code.google.com/p/python-weather-api/
# -*- coding: utf-8 -*-
import os
import pywapi as weather

degree_unit="C"
degree_unit_symbol="*C" # "\xB0C" # "°C"

FtoC=lambda x: "%.0f" % ((float(x)-32.0)*5.0/9.0)

def get_current(google_result):
	current=google_result['current_conditions']
	if "C" in degree_unit:
		return current['temp_c'] + degree_unit_symbol + " and " + current['condition']
	else:
		return current['temp_f'] + degree_unit_symbol + " and " + current['condition']
def get_forecast(google_result, forecast_number = 0):
	forecast=google_result['forecasts'][forecast_number]
	if "C" in degree_unit:
		return forecast['day_of_week']+": "+FtoC(forecast['low'])+"-"+FtoC(forecast['high'])+degree_unit_symbol+" and "+forecast['condition']
	else:
		return forecast['day_of_week']+": "+forecast['low']+"-"+forecast['high']+degree_unit_symbol+" and "+forecast['condition']
#
rows, columns = os.popen('stty size', 'r').read().split() or (40, 132)
google_result = weather.get_weather_from_google('80302')
forecast_number = 0
this_line = "Now: "+get_current(google_result)+"/"+get_forecast(google_result, forecast_number)
last_conditions=google_result['forecasts'][forecast_number]['condition']

while len(this_line) < columns:
	last_line = this_line
	forecast_number += 1
	this_line = last_line+"/"+get_forecast(google_result, forecast_number)
print last_line