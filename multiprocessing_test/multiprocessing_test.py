from multiprocessing import Pool, freeze_support
import time

def f(x):
    time.sleep(0.5)
    return x*x

if __name__ == '__main__':
    freeze_support() # for py2exe
    pool = Pool()

    #result = pool.apply_async(f, (10,))    # evaluate "f(10)" asynchronously
    #print result.get(timeout=1)           # prints "100" unless your computer is *very* slow

    #print pool.map(f, range(10))          # prints "[0, 1, 4,..., 81]"
    result = pool.map_async(f, range(10))
    print "Ready: ", result.ready()
    print "Waiting 6 sec"
    result.wait(timeout = 6)
    print result.get()

    #it = pool.imap_unordered(f, range(10))
    #print it.next()                       # prints "0"
    #print it.next()                       # prints "1"
    #print it.next(timeout=1)              # prints "4" unless your computer is *very* slow
