#!env python
### simple wrapper for WMI that emulates df
from math import floor
import wmi
c = wmi.WMI()

print_block_size=1024.0

print("Filesystem", "%d-blocks" % print_block_size, "Used", "Available", "Capacity", "Caption")
for disk in c.Win32_LogicalDisk(): # DriveType=3):
	size_bytes, avail_bytes = float(disk.Size or 0), float(disk.FreeSpace or 0)
	size, avail = size_byte/print_block_size, size_byte/print_block_size
	use = size-avail
	usepct=100.0*use/size if size > 0 else 1
	print(disk.Name, 
		  floor(size),
		  use,
		  avail,
		  usepct,
		  disk.Caption
		  )