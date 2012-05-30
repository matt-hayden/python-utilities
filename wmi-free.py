#!env python
### simple wrapper for WMI that emulates df
from math import floor

def wmi_free(args = None, machine = None):
	c = wmi.WMI(machine)
	for inst in c.Win32_OperatingSystem():
		if inst.Primary:
			os = inst
			break
	print("", "total", "free")
	
	mtotal, mfree = float(os.TotalVisibleMemorySize), float(os.FreePhysicalMemory)
	mused = mtotal-mfree
	print("Mem", mtotal, mused, mfree)
	
	stotal, sfree = float(os.SizeStoredInPagingFiles), float(os.FreeSpaceInPagingFiles)
	sused = stotal-sfree
	print("Swap", stotal, sused, sfree)
	
#
if __name__ == '__main__':
	try:
		import wmi
	except:
		print("No WMI module")
		print("\t$ pip install WMI")
	else:
		wmi_free()