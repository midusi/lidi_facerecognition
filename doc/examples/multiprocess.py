import multiprocessing
import random
import time


def f1(n):
    while True:
        # random_list=random.sample(list(range(30)),10)
        # l[:]=[]
        # l.extend(random_list)
        # n.foo.bar+=1
        time.sleep(1)
def f2(n):
    while True:
        print(str(n.foo.bar))
        time.sleep(1)


class Foo:
    bar=8
if __name__ == '__main__':

    m=multiprocessing.Manager()
    n=m.Namespace()
    f=Foo()
    n.f=f

    p1=multiprocessing.Process(target=f1,args=(n,))
    p2 = multiprocessing.Process(target=f2,args=(n,))

    p1.start()
    p2.start()