import multiprocessing
import multiprocessing.queues as mpq

class SharedCounter(object):
    """ A synchronized shared counter.

    The locking done by multiprocessing.Value ensures that only a single
    process or thread may read or write the in-memory ctypes object. However,
    in order to do n += 1, Python performs a read followed by a write, so a
    second process may read the old value before the new one is written by the
    first process. The solution is to use a multiprocessing.Lock to guarantee
    the atomicity of the modifications to Value.

    This class comes almost entirely from Eli Bendersky's blog:
    http://eli.thegreenplace.net/2012/01/04/shared-counter-with-pythons-multiprocessing/

    """

    def __init__(self, n = 0):
        self.count = multiprocessing.Value('i', n)

    def increment(self, n = 1):
        """ Increment the counter by n (default = 1) """
        with self.count.get_lock():
            self.count.value += n

    @property
    def value(self):
        """ Return the value of the counter """
        return self.count.value

class Queue():
    def __init__(self):
        self.queue = multiprocessing.Queue()
        self.size = SharedCounter()

    def put(self, item):
        self.size.increment(1)
        self.queue.put(item)

    def get(self):
        self.size.increment(-1)
        return self.queue.get()

    def qsize(self):
        return self.size.value

    def empty(self):
        return not self.qsize()
