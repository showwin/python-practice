import time


def fast_fb(num):
    for i in range(1, num+1):
        st = ''
        if i % 15 == 0:
            st = 'fizzbuzz'
        elif i % 5 == 0:
            st = 'buzz'
        elif i % 3 == 0:
            st = 'fizz'
        else:
            st = i


def slow_fb(num):
    for i in range(1, num+1):
        st = ''
        if i % 3 == 0:
            st += 'fizz'
        if i % 5 == 0:
            st += 'buzz'
        if len(st) == 0:
            st = i

start_time = time.time()
fast_fb(20000)
print(time.time() - start_time)
slow_fb(20000)
print(time.time() - start_time)
