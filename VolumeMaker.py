#!env python
from collections import namedtuple
import os.path
import os
#
filesizes_factory = namedtuple('filesize', ['filename', 'bytes'])
def blocksize_for_bytes(x, blocksize=2048L):
	if not x:
		return 0L
	elif (x % blocksize):
		return blocksize*(long(x/blocksize)+1)
	else:
		return x
class VolumeNotEnoughSpace(Exception):
	pass
class VolumeMaker():
	#
	def __init__(_, size, blocksize=2048):
		_.size = size
		_.blocksize=blocksize
		_.capacity = 0L
		_.filesizes = []

	def add_file(_, filename, size = None, blocksize = None):
		if blocksize is None:
			blocksize = blocksize_for_bytes(os.path.getsize(filename) if size is None else size)
		if blocksize + _.capacity > _.size:
			raise VolumeNotEnoughSpace
		else:
			_.filesizes.append(filesizes_factory(filename, blocksize))
			_.capacity += blocksize
	@property
	def free_bytes(_):
		return _.size - _.capacity
	@property
	def files(_):
		return [ filename for filename, size in _.filesizes ]
	def __len__(_):
		return len(_.filesizes)

	#
def walk(*args):
	#
	volumes = []
	mysize = 2390000
	this_volume = VolumeMaker(size = mysize)
	for root, dirs, files in os.walk(*args):
		filesizes = [ filesizes_factory(basename, os.path.getsize(os.path.join(root, basename))) for basename in files ]
		filesizes.sort(key=lambda x: x.bytes)
		for basename, size in filesizes:
			filename = os.path.join(root, basename)
			if size > this_volume.size:
				# suggest to use a common spanner, maybe p7z
				print "Skipping", filename
			else:
				try:
					this_volume.add_file(filename, size=size)
				except VolumeNotEnoughSpace:
					volumes.append(this_volume)
					this_volume = VolumeMaker(size = mysize)
					this_volume.add_file(filename)
	volumes.append(this_volume)
	return volumes
	#
#
if __name__ == '__main__':
	from sys import argv
	try:
		from os import link
	except:
		from ntfsutils.hardlink import create as link
	#
	target_prefix="5volume_"
	volumes = walk(argv[1])
	print len(volumes), "volumes created of size(s)", " ".join([ "%d" % v.capacity for v in volumes])
	#
	with open("VolumeMaker.log", 'w') as logfo:
		vn = 0
		for v in volumes:
			vn += 1
			target=target_prefix+("%02d" % vn)
			for filename in v.files:
				dirname, basename = os.path.split(filename)
				target_dirname=os.path.join(target,dirname)
				target_filename=os.path.join(target_dirname, basename)
				if not os.path.isdir(target_dirname):
					os.makedirs(target_dirname)
				link(filename, target_filename)
				print >> logfo, target, '\t', filename