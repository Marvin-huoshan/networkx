from multiprocessing import Pool,Process
import os

def f0(x):
    return x * x

def f1(name):
    print('hello',name)

def info(title):
    print(title)
    print('module name:',__name__)
    print('parent process:',os.getppid())
    print('process id',os.getppid())

def f3(name):
    info('function f')
    print('hello',name)

if __name__ == '__main__':
    #with Pool(5) as p:
    #    print(p.map(f0,[1,2,3]))
    #p = Process(target=f1,args=('bob',))
    #p.start()
    #p.join()
    info('main line')
    p = Process(target=f3,args=('bob',))
    p.start()
    p.join()
