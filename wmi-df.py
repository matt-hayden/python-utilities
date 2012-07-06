
import wmi
import sys

DriveType_desc = {	0: "Unknown",
					1: "No Root Directory",
					2: "Removable Disk",
					3: "Local Disk",
					4: "Network Drive",
					5: "Compact Disc",
					6: "RAM Disk" }

def show_mounts(machine=None):
	c = wmi.WMI(machine)
	print >> sys.stderr,  "Warning: logical partitions within a MSDOS extended partition appear to share DeviceID"
	for pl in c.Win32_LogicalDiskToPartition():
		Antecedent, Dependent = pl.Antecedent, pl.Dependent
		flags = []
		if Antecedent.BootPartition:
			flags += "boot",
		if Dependent.Compressed:
			flags += "compressed",
		if Antecedent.PrimaryPartition:
			flags += "primary",
		if Dependent.SupportsDiskQuotas and not Dependent.QuotasDisabled:
			flags += "quota",
		label = Dependent.VolumeName
		print Antecedent.DeviceID, "["+label+"]" if label else "", "on", Dependent.DeviceID, "type", Dependent.FileSystem, "("+" ".join(flags)+")"
def blkid(machine=None):
	c = wmi.WMI(machine)
	print >> sys.stderr,  "Warning: logical partitions within a MSDOS extended partition appear to share DeviceID"
	for pl in c.Win32_LogicalDiskToPartition():
		Antecedent, Dependent = pl.Antecedent, pl.Dependent
		label = Dependent.VolumeName
		print Antecedent.DeviceID, "["+label+"]" if label else "",":","Serial="+Dependent.VolumeSerialNumber if Dependent.VolumeSerialNumber else "", "Type="+Dependent.FileSystem if Dependent.FileSystem else ""
def df(machine=None, block_divisor = 1024.0):
	c = wmi.WMI(machine)
	print >> sys.stderr, "Warning: logical partitions within a MSDOS extended partition appear to share DeviceID"
	print "Filesystem".ljust(40), \
		   "blocks".rjust(11), \
		   "Used".rjust(11), \
		   "Available".rjust(11), \
		   "Capacity".rjust(8), \
		   "Mounted on".ljust(10)
	for pl in c.Win32_LogicalDiskToPartition():
		Antecedent, Dependent = pl.Antecedent, pl.Dependent
		# part_size = float(Antecedent.Size)/block_divisor # reports size of extended partition
		fs_size, avail = float(Dependent.Size or 0)/block_divisor, float(Dependent.FreeSpace or 0)/block_divisor
		used = fs_size - avail
		capacity = 100.0*used/fs_size if fs_size else 100
		label = Dependent.VolumeName
		print (Antecedent.DeviceID + " ["+label+"]" if label else "(unknown)").ljust(40), \
			  ("%d" % fs_size).rjust(11), \
			  ("%d" % used).rjust(11), \
			  ("%d" % avail).rjust(11), \
			  ("%d%%" % capacity).rjust(8), \
			  Dependent.DeviceID.ljust(10)
blkid()
show_mounts()
df(block_divisor=1024*1024)