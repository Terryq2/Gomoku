import multiprocessing
from stones import Stone
import random



def score_line(q) -> float:
        q.put(random.randint(1,4))


if __name__ == '__main__':
    q = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=score_line, args=(q,))
    p2 = multiprocessing.Process(target=score_line, args=(q,))
    p1.start()
    p2.start()

    p1.join()
    p2.join()
    print(q.get())
    print(q.get())
     