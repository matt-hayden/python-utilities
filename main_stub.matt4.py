'''
Description goes here.
'''
from __future__ import with_statement # must be first for python 2.5 or older

from optparse import OptionParser, OptParseError
import os, sys
import fileinput, shutil	# for example below
from tempfile import mkstemp as mktemp	# for example below

class ApplicationError(Exception):
	def __init__(self, msg):
		self.msg = msg

class Usage(ApplicationError):
	def __init__(self, msg):
		self.msg = msg

def main(argv = None):
	'''Parameters
	'''
	unsafe = not __debug__						# if not debugging, cruise through things like overwrite options
	usage = '%prog [options] input [output]'	# customize
	version = '%prog 0.0'						# customize
	
	if not argv:
		argv = sys.argv
	try:
		try:
			parser=OptionParser(usage=usage, 
					    description=__doc__,
					    version=version,
					    conflict_handler='resolve')
			# parser.add_option() defaults to (action='store', type='string')
			'''General options
			'''
			parser.add_option('-q', '--quiet',
					  action='store_false', dest='verbose')
			parser.add_option('-v', '--verbose',
					  action='store_true', dest='verbose',
					  help='Show detailed information (default %default)')
			'''Input options.
			'''
			parser.add_option('--filein',
					  dest='input_filenames', metavar='FILE',
					  help='Multiple occurrances allowed for multiple input files.', action='append')
			'''Output options.
			'''
			parser.add_option('--fileout',
					  dest='output_filename', metavar='FILE',
					  help='specify only one output file')
			parser.add_option('-a', '--args-are-all-input',
					  action='store_true', dest='input_filenames_only',
					  help='Treat all arguments as input filenames, overriding possible "file-in file-out" syntax. (default %default)')
			parser.add_option('-o', '--overwrite',
					  action='store_true', dest='allow_overwrite',
					  help='Overwrite output file')
			parser.add_option('-s', '--no-overwrite',
					  action='store_false', dest='allow_overwrite',
					  help='Stop if the output file exists')
			parser.add_option('-t', '--create-temp',
					  action='store_true', dest='create_temp_output',
					  help='Handle output into a temp file, then move into place. ')
			'''Advanced options. Comment these out if possible.
			'''
			# parser.add_option('-n',
					  # action='store_true', dest='simulation',
					  # help='do nothing (simulation)')
			parser.add_option('--tempfile', 
					  dest='simulation', metavar='FILE',
					  help='Use the specified file as a place to dump output before moving it over the output file.')
			# parser.add_option('--open-mode',
					  # dest='open_mode', choices = ['U', 'r', 'rb', 'rU', 'r+', 'rb+'],
					  # help='file-read operating mode (default %default)')
			# parser.add_option('--save-mode',
					  # dest='save_mode', choices = ['a', 'a+', 'ab', 'ab+', 'w', 'wb', 'w+', 'wb+'],
					  # help='file-write operating mode (default %default)')
			'''Option defaults.
			'''
			parser.set_defaults(allow_overwrite = unsafe,
							    open_mode='rU',		# customize, rU means read with line conversion, b for binary
							    save_mode='w+',		# customize, w+ means write truncate, b for binary
								simulation = False,
								has_input = True,	# False = no input file, stdin (or no input) only
								has_output = True,	# False = no output file, stdout only
							    input_filenames = [],
							    input_filenames_only = True,	# remove to restrict 'prog a b' to read both 'a' and 'b'
								create_temp_output = True,
								tempfile = None,
							    verbose = __debug__)
			options, args = parser.parse_args()
		except OptParseError, err:
			raise Usage(err.msg)
		# Options parsed OK at this point
		#################################################################################
		'''Run-of-the-mill cruncher input scheme
		'''
		v = options.verbose # just an abbreviation
		
		'''Default arg0 arg1 treatment
		'''
		if args:
			if len(args) == 2 \
			   and options.has_output \
			   and not options.input_filenames_only:
				options.input_filenames.append(args[0])
				options.output_filename=args[1]
			else:
				options.input_filenames += args
		else:
			'''No arguments given, so by default parse stdin. fileinput recognizes - as a filename
			'''
			input = [ '-' ]
		
		if options.has_output:
			if options.create_temp_output or options.tempfile:
				'''Note that tempfile.TemporaryFile deletes the file when closed.
				'''
				options.allow_overwrite = True
				options.create_temp_output = True
				if not options.tempfile:
					output_fd, options.tempfile = mktemp()
					# out = os.fdopen(output_fd, options.save_mode) # example of opening via file descriptor
				if v: print "Output used: file descriptor %d to temporary file %s" % (output_fd, options.tempfile)
			if options.allow_overwrite:
				is_valid_output = lambda f: os.path.isfile(f) or not os.path.exists(f)
			else:
				is_valid_output = lambda f: not os.path.exists(f)
			
			if not is_valid_output(options.output_filename):
				raise ApplicationError("cannot output to %s" % options.output_filename)
			if v: print("Output given: %s" % options.output_filename)
			output = options.tempfile
		else:
			'''Options if output is not saved.
			'''
			options.input_filenames_only = True
			output = options.output_filename
		
		if options.has_input:
			is_valid_input = lambda f: os.path.isfile(f) or f in [ '-' ] # modify to take directories as arguments.
			if v: print("Inputs given: %s" % options.input_filenames)
			input = filter(is_valid_input, options.input_filenames)
			if not options.input_filenames:
				raise ApplicationError("no valid input files")
			if v: print("Inputs used: %s" % input)
		#################################################################################
		'''Example variables:
		input						list of input filenames
		output						output filename
		options.output_filename		eventual place to copy the output file
		'''
		#################################################################################
		'''Example like 'cat', but append the filename at the beginning of each line.
		Requires options: has_output, create_temp_output
		'''
		if True:
			fi = fileinput.FileInput(files = input,
									  mode = options.open_mode,
									  openhook=fileinput.hook_compressed)
			if options.simulation:
				for line in fi:
					print "%s: %s" % (fi.filename(), line)
			else:
				with open(output, options.save_mode) as out:
					for line in fi:
						out.write("%s: %s" % (fi.filename(), line))
			fi.close()
		if create_temp_output:
			if v: print "Copying %s to %s" % (output, options.output_filename)
			shutil.move(output, options.output_filename)
		#################################################################################
	# Clean up
	except Usage, err:
		print >>sys.stderr, err.msg
		print >>sys.stderr, 'for help use --help'
		return 4
	except ApplicationError, err:
		print >>sys.stderr, err.msg
		return 2
	except KeyboardInterrupt:
		return 1
	else:
		return 0
if __name__ == '__main__':
	try:
		'''Try importing optional modules.
		psyco is an optimizer http://psyco.sourceforge.net/psycoguide
		'''
		import psyco
		psyco.full()
	except ImportError:
		pass
	sys.exit(main())