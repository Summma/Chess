import multiprocessing as mp
import concurrent.futures
import time


def do(seconds):
    print(f"Sleeping for {seconds} seconds")
    time.sleep(seconds)
    return f"Done... {seconds} seconds"


def recur(depth):
    if depth == 0:
        return 1
    total = 0
    for i in range(10):
        total += recur(depth-1)
    return total


if __name__ == '__main__':
    start = time.perf_counter()

    # Multiprocessing with pooling recursive test
    alpha = list('abcdefghijklmnopqrstuvwxyz')
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(recur, 7) for letter in alpha]

        for f in concurrent.futures.as_completed(results):
            print(f.result())

    # Multiprocessing with pooling
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     secs = range(1, 11)[::-1]
    #     results = [executor.submit(do, sec) for sec in secs]
    #
    #     for f in concurrent.futures.as_completed(results):
    #         print(f.result())

    # Manual Multiprocessing
    # processes = []
    # for _ in range(10):
    #     p = mp.Process(target=do, args=(1,))
    #     p.start()
    #     processes.append(p)
    #
    # for process in processes:
    #     process.join() 1:33:11 - Nope

    print(f"Finished in: {time.perf_counter()-start}")
