#! env python
from os.path import abspath
from windows_clipboard import *
import sys

file_extension = {
	"WAVE": ".wav",
	"ENHMETAFILE": ".wmf",
	"PNG": ".png",
	"JFIF": ".jpeg"
}
#
with clipboard_manager():
	formats = get_clipboard_formats()
	print >> sys.stderr, formats
	if "WAVE" in formats:
		data = clipboard.GetClipboardData(clipboard.CF_WAVE)
	elif "Csv" in formats:
		data = clipboard.GetClipboardData(formats["Csv"])
	elif "ENHMETAFILE" in formats:
		data = clipboard.GetClipboardData(clipboard.CF_ENHMETAFILE)
	elif "PNG" in formats:
		data = clipboard.GetClipboardData(formats["PNG"])
	elif "JFIF" in formats:
		data = clipboard.GetClipboardData(formats["JFIF"])
	elif "CF_HDROP" in formats:
		data = "\n".join(clipboard.GetClipboardData(clipboard.CF_ENHMETAFILECF_HDROP))
	else:
		data = clipboard.GetClipboardData()
	sys.stdout.write(data)