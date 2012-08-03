import aalib
#import Image
import urllib2
from cStringIO import StringIO
from console_size import get_terminal_size

h, w = get_terminal_size()
screen = aalib.AsciiScreen(width=w, height=h)
fp = StringIO(urllib2.urlopen('http://python.org/favicon.ico').read())
#image = Image.open(fp).convert('L').resize(screen.virtual_size)
image = fp
screen.put_image((0, 0), image)
print screen.render()