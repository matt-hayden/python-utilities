#! env python
from windows_clipboard import clipboard, clipboard_manager
import sys

with clipboard_manager():
	if sys.stdin.isatty():
		print "Usage:"
	else:
		#clipboard.SetClipboardText(sys.stdin.read(), clipboard.CF_UNICODETEXT)
		clipboard.SetClipboardData(clipboard.CF_UNICODETEXT, sys.stdin.read())