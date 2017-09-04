import mem_profile
import time

# def square_numbers(nums):
#     for i in nums:
#         yield (i*i)

# my_nums = square_numbers([1,2,3,4,5])

print ('Memory (Before): {}Mb'.format(mem_profile.memory_usage_psutil()))

t1 = time.clock()

my_nums = (x*x for x in xrange(1000000))

#x = list(my_nums) # [1, 4, 9, 16, 25]
x = my_nums # [1, 4, 9, 16, 25]

t2 = time.clock()

print ('Memory (After) : {}Mb'.format(mem_profile.memory_usage_psutil()))
print ('Took {} Seconds'.format(t2-t1))

# for num in my_nums:
#     print num