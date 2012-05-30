#! env python
from Lundh import *
import os.path
import sys
#
for fn in sys.argv[1:]:
	with open(fn,"rb") as fi:
		torrent = decode(fi.read())
	print "Private:", "Yes" if torrent["info"]["private"] else "No"
	print "Pieces: %d x %d bytes" % (len(torrent["info"]["pieces"]), torrent["info"]["piece length"])
	try:
		name = torrent["info"]["name"]
		ext = os.path.splitext(name)[-1]
	except:
		name = "(no name)"
	try:
		size=long(torrent["info"]["length"])
	except:
		size = "(unknown)"
	print name, "%d MB" %(size/1024/1024)
	#
	if "files" in torrent["info"]:
		for file in torrent["info"]["files"]:
			name = os.path.join(file["path"])
			# ext = os.path.splitext(name)[-1]
			size = long(file["length"])
			#print "%d\t%s" % (file["length"], "/".join(file["path"]))
			print name, "%d MB" %(size/1024/1024)
	# else: # single-file torrent
