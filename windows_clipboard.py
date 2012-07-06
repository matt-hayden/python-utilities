#! env python
"""
http://msdn.microsoft.com/en-us/library/windows/desktop/ff729168%28v=vs.85%29.aspx
"""
#from collections import defaultdict
from contextlib import contextmanager
import win32clipboard as clipboard

"""
clipboard_text_formats contains a list of different text formats, in descending
priority.
"""
clipboard_text_formats = (
	clipboard.CF_DSPTEXT,
	clipboard.CF_UNICODETEXT,
	clipboard.CF_TEXT,
	clipboard.CF_OEMTEXT
	)

"""
clipboard_format_names contains a lookup of the constant values in:
	http://msdn.microsoft.com/en-us/library/windows/desktop/ff729168%28v=vs.85%29.aspx
These are apparently not handled by GetClipboardFormatName()
"""
clipboard_format_names = {
	clipboard.CF_BITMAP: "BITMAP",
	clipboard.CF_DIB: "DIB",
	clipboard.CF_DIBV5: "DIBV5",
	clipboard.CF_DIF: "DIF",
	clipboard.CF_DSPBITMAP: "DSPBITMAP",
	clipboard.CF_DSPENHMETAFILE: "DSPENHMETAFILE",
	clipboard.CF_DSPMETAFILEPICT: "DSPMETAFILEPICT",
	clipboard.CF_DSPTEXT: "DSPTEXT",
	clipboard.CF_ENHMETAFILE: "ENHMETAFILE",
	clipboard.CF_HDROP: "CF_HDROP",
	clipboard.CF_LOCALE: "CF_LOCALE",
	clipboard.CF_METAFILEPICT: "METAFILEPICT",
	clipboard.CF_OEMTEXT: "OEMTEXT",
	clipboard.CF_OWNERDISPLAY: "OWNERDISPLAY",
	clipboard.CF_PALETTE: "PALETTE",
	clipboard.CF_PENDATA: "PENDATA",
	clipboard.CF_RIFF: "RIFF",
	clipboard.CF_SYLK: "CF_SYLK",
	clipboard.CF_TEXT: "TEXT",
	clipboard.CF_TIFF: "TIFF",
	clipboard.CF_UNICODETEXT: "UNICODETEXT",
	clipboard.CF_WAVE: "WAVE"
}
#
@contextmanager
def clipboard_manager():
	yield clipboard.OpenClipboard()
	clipboard.CloseClipboard()
#
def clipboard_format_name(enum):
	return clipboard_format_names[enum] if enum in clipboard_format_names else None
#
def get_clipboard_enums(preferred=None):
	"""
	preferred is a tuple containing the order of preferred format enums
	"""
	if preferred:
		enum = clipboard.GetPriorityClipboardFormat(preferred)
		if enum >= 0:
			yield enum
		else:
			raise StopIteration()
	else:
		try:
			i = clipboard.CountClipboardFormats()
			enum = clipboard.EnumClipboardFormats(0)
		except:
			raise StopIteration()
		while i:
			enum = clipboard.EnumClipboardFormats(enum)
			if enum:
				yield enum
			i -= 1
#
def get_clipboard_formats(show_unknown = False):
	"""
	preferred is a tuple containing the order of preferred format enums
	"""
	enums = get_clipboard_enums()
	names = {}
	for e in enums:
		try:
			names[clipboard.GetClipboardFormatName(e)] = e
		except:
			if e in clipboard_format_names:
				names[clipboard_format_names[e]] = e
			elif show_unknown:
				names[e] = e
	return names
#
def is_text(preferred = clipboard_text_formats):
	formats = get_clipboard_formats()
	for f in preferred:
		if f in formats:
			return True
	return False
