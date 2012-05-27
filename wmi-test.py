#!/usr/bin/env python
### Easy-install WMI

### Processes should have the following members:
# CSCreationClassName
# CSName
# Caption
# CommandLine
# CreationClassName
# CreationDate
# Description
# ExecutablePath
# ExecutionState
# Handle
# HandleCount
# InstallDate
# KernelModeTime
# MaximumWorkingSetSize
# MinimumWorkingSetSize
# Name
# OSCreationClassName
# OSName
# OtherOperationCount
# OtherTransferCount
# PageFaults
# PageFileUsage
# ParentProcessId
# PeakPageFileUsage
# PeakVirtualSize
# PeakWorkingSetSize
# Priority
# PrivatePageCount
# ProcessId
# QuotaNonPagedPoolUsage
# QuotaPagedPoolUsage
# QuotaPeakNonPagedPoolUsage
# QuotaPeakPagedPoolUsage
# ReadOperationCount
# ReadTransferCount
# SessionId
# Status
# TerminationDate
# ThreadCount
# UserModeTime
# VirtualSize
# WindowsVersion
# WorkingSetSize
# WriteOperationCount
# WriteTransferCount

import wmi

w=wmi.WMI()
#for p in w.Win32_Process(Name="python.exe"):
#	print p.path()
#	for k, v in sorted(p.properties.iteritems() ):
#		print "\t", k
print '\n'.join(sorted(w.classes))