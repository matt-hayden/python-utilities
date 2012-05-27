"""Convert a CSV file from HOBO into Meter Master format. 
From the HOBO utility, choose to export an Excel text file,
then run this Python script.
"""
import pprint, sys
from optparse import OptionParser

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    usage="%prog [options] [input_hobo_csv [output_mm_csv]]"
    if argv is None:
        argv = sys.argv
    try:
        try:
	    parser=OptionParser(usage=usage, 
				description=__doc__,
				conflict_handler="resolve")
	    parser.set_defaults(verbose=False)
	    # add_option defaults to arguments action="store", type="string",
	    parser.add_option("-q", "--quiet",
			      action="store_false", dest="verbose")
	    parser.add_option("-v", "--verbose",
			      action="store_true", dest="verbose",
			      help="show detailed information"
			      )
	    parser.add_option("--filein",
			      dest="filename_in", metavar="FILE",
			      help="specify input file")
	    parser.add_option("--fileout",
			      dest="filename_out", metavar="FILE",
			      help="specify output file")
	    (options, args) = parser.parse_args()
	    pprint.pprint( (options,args) )
        except parser.error, msg:
             raise Usage(msg)
        # more code
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())