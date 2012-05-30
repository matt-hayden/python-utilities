#!pythoon
from __future__ import with_statement
from os.path import commonprefix, exists, isdir, join, sep, split, splitext
from string import Template
import sys

case_sensitive = False
dry_run = False
overwrite = False
use_alt = True
default_name = "screens"

def avs_joined_source(filenames, source_object_name = "DirectShowSource"):
    return "++".join([ '%s("%s", audio=false)' %(source_object_name,x) for x in filenames])

if case_sensitive:
    fni = sorted(sys.argv[1:],key=str.lower)
else:
    fni = [ x.lower() for x in sys.argv[1:] ]
    fni.sort()
if not fni or len(fni) < 2:
    raise Error("usage")
common = commonprefix(fni)

psep = ''.join((sep, "/"))

if common[-1] in psep or isdir(common):
    root, fno_stub = common, default_name
else:
    root, fno_stub = split(common)
fno_stub = fno_stub.rstrip(" -_.,")
fno = "%s.avs" % fno_stub
alt_fno = "%s_screens.avs" % splitext(fni[0])[0]

# try to determine a
rel_fni = [ x.partition(root)[-1].strip(psep) for x in fni ]

full_fno = join(root, fno)
if exists(full_fno) and not overwrite:
    if use_alt:
        full_fno = join(root,alt_fno)
    else:
        raise Error("%s exists" % fno)

if dry_run:
    print "dry run: would have written ", full_fno
    print avs_joined_source(rel_fni)
    raw_input("<Enter> to continue")
else:    
    with open(full_fno, 'wb') as fo:
        fo.write(avs_joined_source(rel_fni))
#o=raw_input()