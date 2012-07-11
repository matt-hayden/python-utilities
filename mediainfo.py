from datetime import datetime, timedelta
from os.path import exists, normpath, splitunc
import re
from subprocess import check_output, CalledProcessError
import sys
#from xml.dom import minidom
from xml.etree import ElementTree

date_format="%Z %Y-%m-%d %H:%M:%S"
duration_re="((?P<minutes>\d[\d.]*)mn)?\s*((?P<seconds>\d[\d.]*)s)?"
general_units_re="(?P<quantity>\d[\d.]*)+\s*(?P<units>\D+)?"
size_re="(?P<quantity>\d[\d.]*)+\s*(?P<units>[GgMmKk]?(?P<multiplier_style>[Ii])?[Bb])?\s*(?P<fraction>\(\d+%\))?"

duration_parser, general_units_parser, size_parser = re.compile(duration_re), re.compile(general_units_re), re.compile(size_re)

def parse_stream_attribute(tag, text):		
	if tag in ('ID'):
		return int(text)
	# elif tag in ('Bit_rate', 'Overall_bit_rate'):
		# m = general_units_parser.match(text)
		# groups = m.groupdict()
		# if 'quantity' not in groups:
			# return text
		# rate = float(groups['quantity'])
		# try:
			# units_prefix = groups['units'][0].upper()
			# if units_prefix == 'M': rate *= 1000
		# except:
			# pass
		# return rate
	elif tag in ('Duration', 'Source_duration'):
		m = duration_parser.match(text)
		groups = m.groupdict()
		try:	minutes = float(groups['minutes'])
		except:	minutes = 0
		try:	seconds = float(groups['seconds'])
		except:	seconds = 0
		return timedelta(minutes=minutes, seconds=seconds) or text
	# elif tag in ('Height', 'Width', 'Maximum_bit_rate', 'Frame_rate', 'Minimum_frame_rate', 
				 # 'Maximum_frame_rate', 'Bits__Pixel_Frame_', 'Channel_s_', 'Sampling_rate'):
		# m = general_units_parser.match(text)
		# groups = m.groupdict()
		# if 'quantity' in groups:
			# return float(groups['quantity'])
	# elif tag in ('File_size', 'Stream_size', 'Source_stream_size'):
		# """
		# Sizes are very approximate due to MediaInfo output precision.
		# """
		# m = size_parser.match(text)
		# groups = m.groupdict()
		# if 'quantity' not in groups:
			# return text
		# multiplier = 1000
		# if groups['multiplier_style'] in ('i', 'I'):
			# multiplier = 1024
		# size = float(groups['quantity'])*multiplier
		# try:
			# units_prefix = groups['units'][0].upper()
			# if units_prefix == 'G':
				# size *= multiplier**2
			# elif units_prefix == 'M':
				# size *= multiplier
		# except:
			# print >> sys.stderr, "Size string <%s>%s<%s>"%(tag, text, tag), "not parsed"
		# return size
	elif tag in ('Encoded_date', 'Tagged_date'):
		return datetime.strptime(text, date_format) or text
	else:
		return text

def MediaInfo(filenames_in, path_operator = None, call="mediainfo", options = None, filename_seperator = '\x000'):
	options = (options or (), ) + ("--Output=XML",)
	if not path_operator:
		def path_operator(x):
			return normpath(splitunc(x)[-1])
	try:
		xml=check_output((call,)+options+tuple(filenames_in))
	except CalledProcessError as e:
		if exists(fni):
			print >> sys.stderr, "Unknown", mediainfo_cli, "failure"
		else:
			print >> sys.stderr, fni, "not found"
		sys.exit(-1)
	#dom=minidom.parseString(xml)
	parser = ElementTree.XMLParser(encoding="utf-8")
	parser.feed(xml)
	elem = parser.close()
	files = []
	for f in elem:
		tracks = []
		filenames_out = []
		for t in f:
			tracks += (t.attrib['type'], [ (e.tag, parse_stream_attribute(e.tag, e.text)) for e in t ]),
		title = f.text.strip()
		if not title:
			for type,a in tracks:
				filenames_out += [ path_operator(v) for tag,v in a if tag == 'Complete_name' ]
			title = filename_seperator.join( set(filenames_out) )
		files += [ (title, tracks) ]
	# files = [ ( f.text, [ (t.attrib['type'], [ (e.tag, parse_stream_attribute(e.tag, e.text)) for e in t ]) for t in f ] ) for f in elem ]
	return files

if __name__ == '__main__':
	from pprint import pprint
	files = MediaInfo(("../devel/vader_sessions.mov", "earth.mp4"), options=("-f",))
	print len(files), " files read"
	pprint(files)