#!env python
### simple wrapper for WMI that emulates df
import datetime

def wmi_uptime(args = None, machine = None):
	c = wmi.WMI(machine)
	perf = c.Win32_PerfFormattedData_PerfOS_System()
	#itime, btime, ltime = os.InstallDate, os.LastBootUpTime, os.LocalDateTime
	uptime = perf[-1].SystemUpTime
	print datetime.timedelta(seconds=int(uptime))
	
#
if __name__ == '__main__':
	try:
		import wmi
	except:
		print("No WMI module")
		print("\t$ pip install WMI")
	else:
		wmi_uptime()