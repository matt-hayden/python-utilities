#!/usr/bin/python
inputfile = r's:\temp\foo2'

import csv, sys
csv.register_dialect('utorrent', delimiter="\t", quoting=csv.QUOTE_NONE)
inputfile=open(inputfile, "rb")
reader = csv.reader(inputfile, 'utorrent')
# presume we have a header and need to know what order the columns are in
thisrow=reader.next()
try:
        nameFieldNum = thisrow.index('Name')
        sizeFieldNum = thisrow.index('Size')
except ValueError:
        print "value error not in list -- no header?"

sizeFromAbbr = { 'kB': pow(2,10), 'MB': pow(2,20), 'GB': pow(2,30) }
displayUnits='MB'
dvdSize = 4454*sizeFromAbbr['MB']

def convertUnits(value, units=displayUnits):
        "string representing a unit conversion (i.e. from bytes to MB)"
        return "%i %s" % (value/sizeFromAbbr[units], units)
def fullDVDs(value, units=displayUnits):
        "string representing number of full DVDs for a given total size"
        return "%.0f dvds + %s" % (value//dvdSize,convertUnits(value%dvdSize,units))

# initialize variables
total = 0

while thisrow != None:
        try:
                thisrow = reader.next()
        except StopIteration:
                break
        thisname = thisrow[nameFieldNum]
        # add in the size
        thissize = thisrow[sizeFieldNum].split(" ")
        thissize = float(thissize[0])*sizeFromAbbr[thissize[1]]
        total += thissize
        print thisname, convertUnits(thissize), convertUnits(total)
inputfile.close()
print "Total size %s on %s" % (convertUnits(total), fullDVDs(total))
