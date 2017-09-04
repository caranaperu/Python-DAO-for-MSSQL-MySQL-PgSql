import copy
import gc
from memory_profiler import profile

fp = open('memory_profiler_basic_mean.log', 'w+')

@profile(stream=fp)
def function():
    x = list(range(300000))  # allocate a big list
    print(gc.get_count())
    y = copy.deepcopy(x)
    print(gc.get_count())
 #   while x:
 #       x.pop(0)
 #   del x
    del x[:]
    print(gc.get_count())
    gc.collect()
    print(gc.get_count())

    z = list(range(200000))  # allocate a big list
    a = copy.deepcopy(z)
    del z[:]


    b = list(range(200000))  # allocate a big list
    c = copy.deepcopy(z)
    del b[:]
    gc.collect()

    return y

if __name__ == "__main__":
    function()
