#!env python
### simple wrapper for WMI that emulates df
from math import floor

def wmi_df(args = None, machine = None, print_block_size=1024.0):
	c = wmi.WMI(machine)
	print ''.join([ s.rjust(12) for s in ("Filesystem", "%d-blocks" % print_block_size, "Used", "Available", "Capacity", "Caption") ] )
	sizes = dict( [ (disk.Name, int(disk.Size)) for disk in c.Win32_LogicalDisk() if disk.Size ] )
	for disk in c.Win32_PerfFormattedData_PerfDisk_LogicalDisk():
		free = disk.FreeMegabytes or 0
		if disk.Name in sizes:
			size = (sizes[disk.Name] or 0)/1024/1024
			used = size - free
		else:
			size, used = 0, 0
		print ''.join([ str(e).rjust(12) if e else ''.rjust(12) for e in (disk.Name, size, used, free, "%d%%" % disk.PercentFreeSpace, disk.Caption) ] )
	"""
	for disk in c.Win32_LogicalDisk(): # DriveType=3):
		size_bytes, avail_bytes = float(disk.Size or 0), float(disk.FreeSpace or 0)
		size, avail = size_bytes/print_block_size, avail_bytes/print_block_size
		use = size-avail
		usepct=100.0*use/size if size > 0 else 1
		print(disk.Name, 
			  floor(size),
			  use,
			  avail,
			  usepct,
			  disk.Caption
			  )
	"""
#
if __name__ == '__main__':
	try:
		import wmi
	except:
		print("No WMI module")
		print("\t$ pip install WMI")
	else:
		wmi_df()