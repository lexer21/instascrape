import time
from queue import Queue
from threading import Thread

num_threads = 2
process_queue = Queue()


def extract_name(id, q):
    while True:
        txt_data, save_loc = q.get()

        print(f"Processing data, by thread {id}")
        time.sleep(4)
        print(f"Processed data {txt_data}")
        save_loc = txt_data
        q.task_done()


# Setup a thread to fetch data

mydata = None
worker = Thread(target=extract_name, args=(1, process_queue,))
worker.start()
mydict = None

for i in range(10):
    print("Scraping web data...")
    time.sleep(2)

    mydata = [element * i for element in [1, 2, 3, 4, 5]]
    print("Done scraping, sending data to queue for processing")
    process_queue.put((mydata, mydict))

print("Main thread waiting")
process_queue.join()

print("All processing done")

print(mydict)
