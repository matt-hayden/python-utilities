#! env python
"""
Very simply emulate UNIX cal program.
"""

from calendar import TextCalendar
from datetime import datetime
import sys

yearly = False

args=sys.argv[1:]
if args:
	if len(args)>1:
		month, year = int(args[0]), int(args[1])
	else:
		yearly = True
		year = int(args[0])
else:
	now=datetime.now()
	month, year = now.month, now.year

cal=TextCalendar()
if yearly:
	cal.pryear(year)
else:
	cal.prmonth(year, month)