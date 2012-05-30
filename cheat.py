#! python 32
# cheat: man, info, apropos wrapper
import os

filepath_word_sep='_'
#alternate_exts=[ ".txt", ".tab" ]
#
def get_rows_columns(stty_command='stty size', default=(80,43)):
	if sys.stdout.isatty():
		try:
			with os.popen(stty_command or 'stty size', 'r') as pi:
				stty_size=pi.read().split()
		except:
				stty_size=(os.environ["COLUMNS"] if "COLUMNS" in os.environ else default[0],
							os.environ["LINES"]	  if "LINES"   in os.environ else default[1])
		return(stty_size)
	else:
		return((None,)*2)
#
def find_cheatdir(alternate_cheatdirs = None):
	cheatdir_set='CHEATDIR' in os.environ
	# find custom cheat directory
	if cheatdir_set:
		cheatdir=os.environ['CHEATDIR']
		if os.path.isdir(cheatdir):
			return(os.path.abspath(cheatdir)) 
		else:
			user_cheatdir=os.path.expanduser(cheatdir)
			if os.path.isdir(user_cheatdir):
				return(os.path.abspath(user_cheatdir)) 
	else:
		search_cheatdirs=alternate_cheatdirs or [ os.path.expanduser(os.path.join("~",d)) for d in [ "cheats", ".cheats" ] ]
		for d in search_cheatdirs:
			if os.path.isdir(d):
				return(os.path.abspath(d))
	return(None)
#
#
if __name__=='__main__':
	# infopath_set, manpath_set = [ v in os.environ for v in [ 'INFOPATH', 'MANPATH' ] ]
	import sys
	#from which import which
	#
	# cheatdir as a command-line option here
	#
	cheatdir=find_cheatdir()
	#
	if sys.argv[1:]:
		arg_words=filepath_word_sep.join(sys.argv[1:])
		print("arguments:", arg_words)
		#
		target=os.path.join(cheatdir, arg_words)
		if os.path.isdir(target):
			target=os.path.join(target, "{}.py".format(arg_words))
		if os.path.isfile(target):
			rows, columns = get_rows_columns()
			if rows and columns:
				with open(target_file) as fi:
					for l in range(rows):
						print(l, fi.readline().rstrip())
			else:
				print(target, "will become output")
		else:
			print(target, "is not a file")
	#