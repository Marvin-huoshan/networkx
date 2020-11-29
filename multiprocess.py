from multiprocessing import Pool,Process
import os,time,random

def run_proc(name):
    print('Run child process %s (%s)...' % (name,os.getppid()))

def long_time_task(name):
    print('Run task %s (%s)...' % (name,os.getppid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print('Task %s run %0.2f seconds.' % (name,(end - start)))

if __name__ == '__main__':
    print('Parent process %s.' % os.getppid())
    p = Pool(4)
    for i in range(5):
        p.apply_async(long_time_task,args=(i,))
    print('Waitiong for all subprocess done...')
    p.close()
    p.join()
    print('All subprocess done.')
