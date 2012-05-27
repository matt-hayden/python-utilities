#!python
from __future__ import with_statement
import glob, os, string, sys, wx

# options
delimiter="\t"
comment_prefix="\t"

# command-line parameters
parameters=sys.argv
sourcefile = parameters[1]
filenames = parameters[2:]

# the extension determines AviSynth behaviour
sourcefile_type=os.path.splitext(sourcefile)[-1]
# Newlines at the end, please
avs_script_header= \
{	".avi":string.Template("""# Requires AviSynth and $filename
source=AviSource("$filename", audio=false)
"""), \
	".mpg":string.Template("""# Requires AviSynth and $filename
source=DirectShowSource("$filename", audio=false)
"""), \
	".wmv":string.Template("""# Requires AviSynth and $filename
source=DirectShowSource("$filename", audio=false)
""")}[sourcefile_type]

avs_script_line=string.Template("""source.Trim($begin, $end)
""")

# try to get a common name for the set
split_scene_filename_pattern=os.path.commonprefix(parameters).strip()
if not split_scene_filename_pattern: # uh oh
	split_scene_filename_pattern = os.path.split(os.path.realpath('.'))[-1:]

if not split_scene_filename_pattern:
	split_scene_filename_pattern = sourcefile

# ... and interactively verify
gui = wx.PySimpleApp()
gui_title = "Python"
text_entry = wx.TextEntryDialog(None, 
"""Modify filename prefix
Example: foo. results in foo.x.avs""", gui_title, " ".join(split_scene_filename_pattern))
assert text_entry.ShowModal() == wx.ID_OK
split_scene_filename_pattern = text_entry.GetValue()
assert split_scene_filename_pattern
gui.Exit()
# fix the output filename pattern
split_scene_filename=string.Template("%s$scene.avs" % split_scene_filename_pattern)

# processing begins
splits={}
previous_end=0

for filename in filenames:
	print "%sBeginning %s" % (comment_prefix, filename)
	with open(filename) as f:
		print "%sOpening %s" % (comment_prefix, filename)
		for line in f:
			print "%sProcessing %s" % (comment_prefix, line)
			begin, name, end = line.strip("\n").split(delimiter)
			if not begin: begin=previous_end
			if not end: end=0
			if not splits.has_key(name):
				splits[name]=avs_script_header.substitute(filename=sourcefile)
			splits[name] += avs_script_line.substitute(begin=begin, end=end)
			previous_end=end
		print "%s%s done." % (comment_prefix, filename)
for trackname, code in splits.iteritems():
	with open(split_scene_filename.substitute(scene=trackname),"a") as output:
		output.write(code)
print "%sDone." % (comment_prefix)