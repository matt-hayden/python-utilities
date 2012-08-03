
import wmi
c=wmi.WMI()

pfu = c.Win32_PageFileUsage()
for inst in pfu:
	print inst.AllocatedBaseSize, inst.CurrentUsage, inst.Name