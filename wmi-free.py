#!env python
### simple wrapper for WMI that emulates df
from math import floor

def wmi_free(args = None, machine = None):
	width=12
	c = wmi.WMI(machine)
	for inst in c.Win32_OperatingSystem():
		if inst.Primary:
			os = inst
			break
	print "".ljust(width), \
	      "total".rjust(width), \
	      "used".rjust(width), \
		  "free".rjust(width)
	
	mtotal, mfree = int(os.TotalVisibleMemorySize), int(os.FreePhysicalMemory)
	mused = mtotal-mfree
	print "Mem".ljust(width), \
	      str(mtotal).rjust(width), \
		  str(mused).rjust(width), \
		  str(mfree).rjust(width)
	stotal, sfree = int(os.SizeStoredInPagingFiles), int(os.FreeSpaceInPagingFiles)
	sused = stotal-sfree
	print "Swap".ljust(width), \
	      str(stotal).rjust(width), \
		  str(sused).rjust(width), \
		  str(sfree).rjust(width)
	
#
if __name__ == '__main__':
	import sys
	try:
		import wmi
	except:
		print("No WMI module")
		print("\t$ pip install WMI")
		sys.exit(-1)
	wmi_free()