import ctypes
import os.path

Wintrust = ctypes.WinDLL('Wintrust.DLL')
_IsCatalogFile = Wintrust['IsCatalogFile']
def IsCatalogFile(handle = None, filename = None):
	return _IsCatalogFile(handle, filename)
if __name__ == '__main__':
	for root, dirs, files in os.walk('.'):
		for fn in [ os.path.join(root,fn) for fn in files if os.path.splitext(fn)[-1].upper() == '.CAT' ]:
			afn = unicode(os.path.abspath(fn))
			print IsCatalogFile(filename = afn), afn