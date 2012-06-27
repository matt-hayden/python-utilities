#! env python
"""
Wrapper to get the size of the current terminal window. Availability:
UNIX: curses and console tools
Win32: PyWin32 undocumented
"""
def get_win32console_size():
	"""
	http://nullege.com/codes/search/win32console.GetStdHandle
	"""
	try:
		import win32console
	except:
		return None
	# Query stderr to avoid problems with redirections
	screenbuf = win32console.GetStdHandle(win32console.STD_ERROR_HANDLE)
	window = screenbuf.GetConsoleScreenBufferInfo()['Window']
	columns = window.Right - window.Left + 1
	rows = window.Bottom - window.Top + 1
	return (rows, columns)
#
def get_termios_size():
	"""
	http://pdos.csail.mit.edu/~cblake/cls/cls.py
	"""
	def ioctl_GWINSZ(fd):              #### TABULATION FUNCTIONS
		try:                                ### Discover terminal width
			import fcntl, termios, struct, os
			cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
		except:
			return None
		return cr
	cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)  # try open fds
	if not cr:                                                  # ...then ctty
		try:
			fd = os.open(os.ctermid(), os.O_RDONLY)
			cr = ioctl_GWINSZ(fd)
			os.close(fd)
		except:
			return None
	return cr[1], cr[0]
#
def get_terminal_size(default = None):
	rc = get_termios_size()
	if not rc:
		try:
			rc = os.popen('stty size', 'r').read().split()
		except:
			pass
	if not rc:
		rc = get_win32console_size()
	if not rc:
		rc = env['LINES'], env['COLUMNS']
	return rc or default
#