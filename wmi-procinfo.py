#!env python
### simple wrapper for WMI that emulates df
from math import floor

wmi_Win32_Processor_Architecture_code = {
	0:	"x86",
	1:	"MIPS",
	2:	"Alpha",
	3:	"PowerPC",
	6:	"Itanium-based systems",
	9:	"x64"
}
wmi_Win32_Processor_VoltageCaps_bits = {
	1:	5.0,
	2:	3.3,
	4:	2.9
}

def wmi_procinfo(args = None, machine = None):
	sep = ": "
	width = 25
	hexformat = "%#0.8x"
	c = wmi.WMI(machine)
	for p in c.Win32_Processor():
		print(p.DeviceID, ":")
		if p.AddressWidth:
			print("AddressWidth".ljust(width), sep, p.AddressWidth)
		print("Architecture".ljust(width), sep, wmi_Win32_Processor_Architecture_code[p.Architecture])
		if p.Availability not in (2,6):
			print("Availability".ljust(width), sep, p.Availability)
		if p.Caption != p.Description:
			print("Caption".ljust(width), sep, p.Caption)
		if p.ConfigManagerErrorCode:
			print("ConfigManagerErrorCode", sep, p.ConfigManagerErrorCode)
		# print("ConfigManagerUserConfig", sep, p.ConfigManagerUserConfig)
		if p.CpuStatus:
			print("CpuStatus".ljust(width), sep, p.CpuStatus)
		print("Current Clock Speed".ljust(width), sep, "%d MHz" % p.CurrentClockSpeed)
		print("Current Voltage".ljust(width), sep, "%1.3f V" % (float(p.CurrentVoltage)/10.0) )
		print("DataWidth".ljust(width), sep, p.DataWidth)
		print("Description".ljust(width), sep, p.Description)
		# print("ErrorCleared", sep, p.ErrorCleared)
		# print("ErrorDescription", sep, p.ErrorDescription)
		print("External Clock Speed".ljust(width), sep, "%d MHz" % p.ExtClock)
		if p.Family == 1:
			print("OtherFamilyDescription".ljust(width), sep, p.OtherFamilyDescription)
		elif p.Family != 2:
			print("Family".ljust(width), sep, p.Family)
		# print("InstallDate", sep, p.InstallDate)
		print("L2 Cache Size".ljust(width), sep, "%d KB" % p.L2CacheSize)
		if p.L2CacheSpeed:
			print("L2 Cache Speed".ljust(width), sep, "%d MHz" % p.L2CacheSpeed)
		# p.L3CacheSize, p.L3CacheSpeed are Vista and later
		# print("LastErrorCode", sep, p.LastErrorCode)
		print("Level".ljust(width), sep, p.Level)
		if p.LoadPercentage:
			print("LoadPercentage".ljust(width), sep, float(p.LoadPercentage))
		print("Manufacturer".ljust(width), sep, p.Manufacturer)
		print("Max Clock Speed".ljust(width), sep, "%d MHz" % p.MaxClockSpeed)
		print("Name".ljust(width), sep, p.Name)
		print("NumberOfCores".ljust(width), sep, p.NumberOfCores)
		print("NumberOfLogicalProcessors".ljust(width), sep, p.NumberOfLogicalProcessors)
		if p.PNPDeviceID:
			print("PNPDeviceID".ljust(width), sep, p.PNPDeviceID)
		print("PowerManagementSupported".ljust(width), sep, p.PowerManagementSupported)
		# p.PowerManagementCapabilities[]
		if p.ProcessorId:
			eax1=int(p.ProcessorId[:8], 16)
			print("Signature".ljust(width), sep, hexformat % eax1)
			edx=int(p.ProcessorId[-8:], 16)
			print("Features".ljust(width), sep, hexformat % edx)
		if p.ProcessorType != 2:
			print("ProcessorType".ljust(width), sep, p.ProcessorType)
		print("Revision".ljust(width), sep, p.Revision)
		print("Role".ljust(width), sep, p.Role)
		print("SocketDesignation".ljust(width), sep, p.SocketDesignation)
		print("Status".ljust(width), sep, p.Status)
		if p.StatusInfo not in (2, 5):
			print("StatusInfo".ljust(width), sep, p.StatusInfo)
		print("Stepping".ljust(width), sep, p.Stepping)
		# print("SystemName".ljust(width), sep, p.SystemName)
		if p.UniqueId:
			print("UniqueId".ljust(width), sep, p.UniqueId)
		if p.UpgradeMethod not in (2, 6):
			print("UpgradeMethod".ljust(width), sep, p.UpgradeMethod)
		print("Version".ljust(width), sep, p.Version)
		if p.VoltageCaps:
			try:
				vcc = int(p.VoltageCaps)
				VoltageCaps_decoded = [ "%1.3f V" % v for k, v in wmi_Win32_Processor_VoltageCaps_bits.iteritems() if vcc & k ]
				print("VoltageCaps".ljust(width), sep, ", ".join(VoltageCaps_decoded))
			except:
				print("VoltageCaps".ljust(width), sep, p.VoltageCaps)
		print()
#
if __name__ == '__main__':
	try:
		import wmi
	except:
		print("No WMI module")
		print("\t$ pip install WMI")
	else:
		wmi_procinfo()