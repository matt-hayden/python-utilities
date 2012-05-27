from os import linesep
from py7zlib import Archive7z, ArchiveError
import string

CSV_extensions = u'.CSV;.TXT;.TSV;.TAB'.split(u';')
size_threshold = 2**26

p7z_pathsep = u'/'

def is_CSV_extension(filename,
                     extensions = CSV_extensions):
    if filename:
        filename = filename.upper()
        for ext in extensions:
            if filename.endswith(ext):
                return True
    return False
def is_attr_extension(filename):
    return filename.upper().endswith('.INI')
    
fi=open("foo+with_directory.7z",'rb')
zfi=Archive7z(fi)

if False:
    print "size, CRC, name:"
    zfi.list()
    membernames=zfi.getnames()
    print "members:", membernames
    csv_members=filter(is_CSV_extension, membernames)
    csv_members.sort(key=string.upper)
    print "csv_members:", csv_members
    for mn in csv_members:
        member = zfi.getmember(mn).read()
        print mn, "len", len(member)
        if linesep in member:
            contents = member.split(linesep)
        else:
            contents = member.split(r'\n')
        print mn, "len:", len(member), "lines:", len(contents)
if True:
    print "Archive is %ssolid" % ('' if zfi.solid else 'not ')
    if zfi.numfiles > 0:
        members = zfi.getmembers()
        maxsize = max([m.size for m in members])
        print "largest file size:", maxsize
        csv_members = filter(lambda m: is_CSV_extension(m.filename), members)
        print len(csv_members), "csv files found"
        reasonably_sized_csv_members = filter(lambda m: m.size < size_threshold, csv_members)
        print len(reasonably_sized_csv_members), "reasonably sized CSV files found"
        for m in members:
            contents = m.read()
            print m.filename, "is size", len(contents)
            if linesep in contents:
                contents = contents.split(linesep)
            else:
                contents = contents.split(r'\n')
            print m.filename, "has", len(contents), "lines"
            
    
fi.close()