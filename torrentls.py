#! env python
from Lundh import *
import sys
#
for fn in sys.argv[1:]:
	with open(fn,"rb") as fi:
		torrent = decode(fi.read())
		for file in torrent["info"]["files"]:
			print "%d\t%s" % (file["length"], "/".join(file["path"]))