#!env python
### simple wrapper for WMI that emulates df
from math import floor

DriveType_desc = {	0: "Unknown",
					1: "No Root Directory",
					2: "Removable Disk",
					3: "Local Disk",
					4: "Network Drive",
					5: "Compact Disc",
					6: "RAM Disk" }


def wmi_df(args = None, machine = None, print_block_size=1024.0):
	c = wmi.WMI(machine)
	print("Filesystem", "%d-blocks" % print_block_size, "Used", "Available", "Capacity", "Caption")
	for disk in c.Win32_LogicalDisk(DriveType=3):
		size_bytes, avail_bytes = float(disk.Size or 0), float(disk.FreeSpace or 0)
		size, avail = size_bytes/print_block_size, avail_bytes/print_block_size
		use = size-avail
		usepct=100.0*(use/size) if size > 0 else 1
		print(disk.Name, 
			  floor(size),
			  use,
			  avail,
			  "%d%%" % usepct,
			  disk.Caption
			  )
#
if __name__ == '__main__':
	try:
		import wmi
	except:
		print("No WMI module")
		print("\t$ pip install WMI")
	else:
		wmi_df()