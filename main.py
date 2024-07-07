from fastapi import FastAPI , Query , Path , Body
from pydantic import BaseModel
import threading
import random
from typing import List,Optional
import time
from queue import Queue
import multiprocessing
import datetime
from threading import Barrier
from multiprocessing import Process, Queue, current_process
from multiprocessing import Barrier
from multiprocessing import Pool
import json



app = FastAPI()

output_messages = []

# 1:
def my_func(thread_number: int):
    message = f"my_func called by thread N°{thread_number}"
    output_messages.append(message)

class ThreadCount(BaseModel):
    thread_count: int
@app.post("/body1/")
async def body_scenario(thread_count: ThreadCount):
    global output_messages
    output_messages = []
    threads = []
    for i in range(thread_count.thread_count):
        thread = threading.Thread(target=my_func, args=(i,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    return output_messages

@app.post("/body2/")
async def body_scenario(thread_count: ThreadCount):
    global output_messages
    output_messages = []
    threads = []
    for i in range(thread_count.thread_count):
        thread = threading.Thread(target=my_func, args=((thread_count.thread_count - 1) - i,))
        threads.append(thread)
        thread.start()
        thread.join()

    return output_messages


@app.post("/body3/")
async def body_scenario(thread_count: ThreadCount):
    global output_messages
    output_messages = []
    threads = []

    half_count = thread_count.thread_count // 2

    for i in range(half_count, thread_count.thread_count):
        thread = threading.Thread(target=my_func, args=(i,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    threads = []
    for i in range(half_count):
        thread = threading.Thread(target=my_func, args=(i,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    return output_messages


# 2:
def function_A():
    global output_messages
    output_messages.append("function_A--> starting")
    time.sleep(1)
    output_messages.append("function_A--> exiting")

def function_B():
    global output_messages
    output_messages.append("function_B--> starting")
    time.sleep(3)
    output_messages.append("function_B--> exiting")

def function_C():
    global output_messages
    output_messages.append("function_C--> starting")
    time.sleep(2)
    output_messages.append("function_C--> exiting")


@app.get("/path1/{thread_count}")
async def path_thread(thread_count: int = Path(..., title="Number of Threads", ge=1, le=3)):
    global output_messages
    output_messages = []
    threads = []
    functions = [function_A, function_B, function_C]
    for i in range(thread_count):
        thread = threading.Thread(target=functions[i])
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    return output_messages

@app.get("/path2/{thread_count}")
async def path_thread(thread_count: int = Path(..., title="Number of Threads", ge=1, le=3)):
    global output_messages
    output_messages = []
    threads = []
    functions = [function_A, function_B, function_C]
    for i in range(thread_count):
        thread = threading.Thread(target=functions[i])
        threads.append(thread)
        thread.start()
        thread.join()

    return output_messages

@app.get("/path3/{thread_count}")
async def path_thread(thread_count: int = Path(..., title="Number of Threads", ge=1, le=3)):
    global output_messages
    output_messages = []
    threads = []

    thread_A = threading.Thread(target=function_A)
    thread_B = threading.Thread(target=function_B)
    thread_C = threading.Thread(target=function_C)

    threads.append(thread_C)
    thread_C.start()
    thread_C.join()
    threads.append(thread_B)
    thread_B.start()
    thread_B.join()
    threads.append(thread_A)
    thread_A.start()
    thread_A.join()

    return output_messages


# 3:
class MyThread(threading.Thread):
    def __init__(self, thread_id, sleep_time):
        super().__init__()
        self.thread_id = thread_id
        self.sleep_time = sleep_time

    def run(self):
        global output_messages
        output_messages.append(f"---> Thread#{self.thread_id} running, belonging to process ID {threading.current_thread().ident}")
        time.sleep(self.sleep_time)
        output_messages.append(f"---> Thread#{self.thread_id} over")

class ThreadInput(BaseModel):
    thread_id: int
    sleep_time: float

@app.post("/body4/")
async def run_threads(thread_inputs: list[ThreadInput] = Body(...)):
    threads = []
    global output_messages
    output_messages = []

    start_time = time.time()

    for thread_input in thread_inputs:
        thread = MyThread(thread_input.thread_id, thread_input.sleep_time)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time

    output_messages.append("End")
    output_messages.append(f"--- {total_time} seconds ---")

    return output_messages

@app.post("/body5/")
async def run_threads(thread_inputs: list[ThreadInput] = Body(...)):
    threads = []
    global output_messages
    output_messages = []

    start_time = time.time()

    for thread_input in thread_inputs:
        thread = MyThread(thread_input.thread_id, thread_input.sleep_time)
        thread.start()
        threads.append(thread)
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time

    output_messages.append("End")
    output_messages.append(f"--- {total_time} seconds ---")

    return output_messages

@app.post("/body6/")
async def run_threads(thread_inputs: list[ThreadInput] = Body(...)):
    threads = []
    global output_messages
    output_messages = []

    start_time = time.time()

    for thread_input in thread_inputs:
        if thread_input.thread_id <= 5:
            thread = MyThread(thread_input.thread_id, thread_input.sleep_time)
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()

    for thread_input in thread_inputs:
        if thread_input.thread_id > 5:
            thread = MyThread(thread_input.thread_id, thread_input.sleep_time)
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time

    output_messages.append("End")
    output_messages.append(f"--- {total_time} seconds ---")

    return {"output": output_messages}


# 4:
lock = threading.Lock()

class MyThread_2(threading.Thread):
    def __init__(self, thread_id):
        super().__init__()
        self.thread_id = thread_id

    def run(self):
        global output_messages
        global lock

        with lock:
            output_messages.append(
                f"---> Thread#{self.thread_id} running, belonging to process ID {threading.current_thread().ident}")

        time.sleep(1)

        with lock:
            output_messages.append(f"---> Thread#{self.thread_id} over")

class MyThread_3(threading.Thread):
    def __init__(self, thread_id):
        super().__init__()
        self.thread_id = thread_id

    def run(self):
        global output_messages
        global lock

        lock.acquire()
        try:
            output_messages.append(
                f"---> Thread#{self.thread_id} running, belonging to process ID {threading.current_thread().ident}")
        finally:
            lock.release()

        time.sleep(1)

        lock.acquire()
        try:
            output_messages.append(f"---> Thread#{self.thread_id} over")
        finally:
            lock.release()



@app.get("/query1/")
async def run_threads():
    global output_messages
    output_messages = []
    threads = []

    start_time = time.time()

    for i in range(1, 10):
        thread = MyThread_2(i)
        thread.start()
        threads.append(thread)
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time

    output_messages.append("End")
    output_messages.append(f"--- {total_time} seconds ---")

    return output_messages

@app.get("/query2/")
async def run_threads():
    global output_messages
    output_messages = []
    threads = []

    start_time = time.time()

    for i in range(1, 10):
        thread = MyThread_2(i)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time

    output_messages.append("End")
    output_messages.append(f"--- {total_time} seconds ---")

    return output_messages

@app.get("/query3/")
async def run_threads():
    global output_messages
    output_messages = []
    threads = []

    start_time = time.time()

    for i in range(1, 10):
        thread = MyThread_2(10 - i)
        thread.start()
        threads.append(thread)
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time

    output_messages.append("End")
    output_messages.append(f"--- {total_time} seconds ---")

    return output_messages


#5:
class MyThread_4(threading.Thread):
    def __init__(self, thread_id, shared_data, lock):
        super().__init__()
        self.thread_id = thread_id
        self.shared_data = shared_data
        self.lock = lock

    def run(self):
        while True:
            with self.lock:
                if self.shared_data["items_to_add"] > 0:
                    self.shared_data["output_messages"].append(
                        f"ADDED one item --> {self.shared_data['items_to_add'] - 1} item to ADD"
                    )
                    self.shared_data["items_to_add"] -= 1
                    time.sleep(0.5)
                if self.shared_data["items_to_remove"] > 0:
                    self.shared_data["output_messages"].append(
                        f"REMOVED one item --> {self.shared_data['items_to_remove'] - 1} item to REMOVE"
                    )
                    self.shared_data["items_to_remove"] -= 1
                    time.sleep(0.5)
                else:
                    break

@app.get("/query4/")
async def process_items(items_to_add: int = Query(..., title="Items to Add"),
                        items_to_remove: int = Query(..., title="Items to Remove")):
    lock = threading.RLock()
    shared_data = {
        "items_to_add": items_to_add,
        "items_to_remove": items_to_remove,
        "output_messages": []
    }

    shared_data["output_messages"].append(f"N° {items_to_add} items to ADD")
    shared_data["output_messages"].append(f"N° {items_to_remove} items to REMOVE")

    threads = []
    for i in range(items_to_add):
        thread = MyThread_4(i + 1, shared_data, lock)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return shared_data["output_messages"]

class MyThread_5(threading.Thread):
    def __init__(self, thread_id, shared_data, lock):
        super().__init__()
        self.thread_id = thread_id
        self.shared_data = shared_data
        self.lock = lock

    def run(self):
        add_counter = 0  # شمارنده برای تعداد عملیات ADD

        while True:
            with self.lock:
                if self.shared_data["items_to_add"] > 0:
                    self.shared_data["output_messages"].append(
                        f"ADDED one item --> {self.shared_data['items_to_add'] - 1} item to ADD"
                    )
                    self.shared_data["items_to_add"] -= 1
                    add_counter += 1
                    time.sleep(0.5)

                    # بررسی برای انجام عملیات REMOVE هر 6 عملیات ADD
                    if add_counter == 6 and self.shared_data["items_to_remove"] > 0:
                        self.shared_data["output_messages"].append(
                            f"REMOVED one item --> {self.shared_data['items_to_remove'] - 1} item to REMOVE"
                        )
                        self.shared_data["items_to_remove"] -= 1
                        add_counter = 0  # تنظیم مجدد شمارنده برای ADD به صفر
                        time.sleep(0.5)

                elif self.shared_data["items_to_remove"] > 0:
                    self.shared_data["output_messages"].append(
                        f"REMOVED one item --> {self.shared_data['items_to_remove'] - 1} item to REMOVE"
                    )
                    self.shared_data["items_to_remove"] -= 1
                    time.sleep(0.5)
                else:
                    break

@app.get("/query5/")
async def process_items(items_to_add: int = Query(..., title="Items to Add"),
                        items_to_remove: int = Query(..., title="Items to Remove")):
    lock = threading.RLock()
    shared_data = {
        "items_to_add": items_to_add,
        "items_to_remove": items_to_remove,
        "output_messages": []
    }

    shared_data["output_messages"].append(f"N° {items_to_add} items to ADD")
    shared_data["output_messages"].append(f"N° {items_to_remove} items to REMOVE")

    threads = []
    for i in range(items_to_add):
        thread = MyThread_5(i + 1, shared_data, lock)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return shared_data["output_messages"]

class MyThread_6(threading.Thread):
    def __init__(self, thread_id, shared_data, lock):
        super().__init__()
        self.thread_id = thread_id
        self.shared_data = shared_data
        self.lock = lock

    def run(self):
        while True:
            with self.lock:
                if self.shared_data["items_to_add"] > 0:
                    self.shared_data["output_messages"].append(
                        f"ADDED one item --> {self.shared_data['items_to_add'] - 1} item to ADD"
                    )
                    self.shared_data["items_to_add"] -= 1
                    time.sleep(0.5)
                elif self.shared_data["items_to_remove"] > 0:
                    self.shared_data["output_messages"].append(
                        f"REMOVED one item --> {self.shared_data['items_to_remove'] - 1} item to REMOVE"
                    )
                    self.shared_data["items_to_remove"] -= 1
                    time.sleep(0.5)
                else:
                    break

@app.get("/query6/")
async def process_items(items_to_add: int = Query(..., title="Items to Add"),
                        items_to_remove: int = Query(..., title="Items to Remove")):
    lock = threading.RLock()
    shared_data = {
        "items_to_add": items_to_add,
        "items_to_remove": items_to_remove,
        "output_messages": []
    }

    shared_data["output_messages"].append(f"N° {items_to_add} items to ADD")
    shared_data["output_messages"].append(f"N° {items_to_remove} items to REMOVE")

    threads = []
    total_operations = items_to_add + items_to_remove

    for i in range(total_operations):
        thread = MyThread_6(i + 1, shared_data, lock)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return shared_data["output_messages"]

# 6:
semaphore = threading.Semaphore(0)
max_notifications = 10
output_list = []
output_list_lock = threading.Lock()

class Producer(threading.Thread):
    def run(self):
        for _ in range(max_notifications):
            time.sleep(1)
            item_number = random.randint(100, 999)
            with output_list_lock:
                output_list.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
                                   f"{self.name} INFO Producer notify: item number {item_number}")
            semaphore.release()  # Notify one consumer

class Consumer(threading.Thread):
    def run(self):
        for _ in range(max_notifications):
            with output_list_lock:
                output_list.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
                                   f"{self.name} INFO Consumer is waiting")
            semaphore.acquire()  # Wait for a notification
            with output_list_lock:
                # Process the item
                last_notification = next(
                    (msg for msg in reversed(output_list) if "Producer notify" in msg), None
                )
                if last_notification:
                    item_number = last_notification.split()[-1]
                    output_list.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
                                       f"{self.name} INFO Consumer notify: item number {item_number}")

@app.get("/produce-consume_1/", response_model=List[str])
async def produce_consume(
    num_producers: Optional[int] = Query(default=1, ge=1, le=10),
    num_consumers: Optional[int] = Query(default=1, ge=1, le=10)
):
    global output_list
    output_list = []

    # Start consumer threads
    consumers = []
    for i in range(num_consumers):
        consumer = Consumer(name=f"Thread-{i*2+1}")
        consumers.append(consumer)
        consumer.start()

    # Start producer threads
    producers = []
    for i in range(num_producers):
        producer = Producer(name=f"Thread-{i*2+2}")
        producers.append(producer)
        producer.start()

    for producer in producers:
        producer.join()

    for consumer in consumers:
        consumer.join()

    return output_list



semaphore_items = threading.Semaphore(0)  # کنترل دسترسی مصرف‌کنندگان به آیتم‌ها
semaphore_producers_done = threading.Semaphore(0)  # اطمینان از اتمام تولیدکنندگان
max_notifications = 5
output_list_2 = []
output_list_lock_2 = threading.Lock()
item_queue = Queue()

class Producer_2(threading.Thread):
    def run(self):
        for _ in range(max_notifications):
            time.sleep(1)
            item_number = random.randint(100, 999)
            with output_list_lock_2:
                output_list_2.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
                                   f"{self.name} INFO Producer notify: item number {item_number}")
                item_queue.put(item_number)
            semaphore_items.release()  # Notify one consumer
        semaphore_producers_done.release()  # Signal producer is done

class Consumer_2(threading.Thread):
    def run(self):
        # Wait for all producers to finish
        semaphore_producers_done.acquire()
        for _ in range(max_notifications):
            semaphore_items.acquire()  # Wait for a notification
            item_number = item_queue.get()
            with output_list_lock_2:
                output_list_2.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} "
                                   f"{self.name} INFO Consumer notify: item number {item_number}")

@app.get("/produce-consume_2/", response_model=List[str])
async def produce_consume(
    num_producers: Optional[int] = Query(default=1, ge=1, le=10),
    num_consumers: Optional[int] = Query(default=1, ge=1, le=10)
):
    global output_list_2
    output_list_2 = []
    item_queue.queue.clear()  # Clear the queue for new run

    producers_2 = []
    for i in range(num_producers):
        producer = Producer_2(name=f"Thread-{i*2+2}")
        producers_2.append(producer)
        producer.start()
    for producer in producers_2:
        producer.join()

    # Signal consumers that producers are finished
    semaphore_producers_done.release()

    consumers_2 = []
    for i in range(num_consumers):
        consumer = Consumer_2(name=f"Thread-{i*2+1}")
        consumers_2.append(consumer)
        consumer.start()
    for consumer in consumers_2:
        consumer.join()

    return output_list_2



# 7:

barrier = Barrier(3)  # Create a barrier for 3 threads

def race_participant(name):
    output_messages.append(f"{name} reached the barrier at: {datetime.datetime.now()}")
    barrier.wait()
    output_messages.append(f"{name} passed the barrier at: {datetime.datetime.now()}")

@app.get("/barrier_1")
async def start_race():
    global output_messages
    output_messages = []
    output_messages.append("START RACE!!!!")

    # Define participants
    participants = ["Dewey", "Huey", "Louie"]
    threads = []

    for participant in participants:
        thread = threading.Thread(target=race_participant, args=(participant,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    output_messages.append("Race over!")

    return output_messages

# ////////////////////////////////////////////////////////////////////////////////////////////////////


# 1:

def myFunc(n, idx, shared_list):
    output = []
    output.append(f"calling myFunc from process n°: {idx}")
    for i in range(n):
        output.append(f"output from myFunc is :{i}")
    shared_list[idx] = output
@app.get("/calculate")
async def calculate(
    n0: int = Query(...),
    n1: int = Query(...),
    n2: int = Query(...),
    n3: int = Query(...),
    n4: int = Query(...),
    n5: int = Query(...)
):
    inputs = [n0, n1, n2, n3, n4, n5]
    manager = multiprocessing.Manager()
    shared_list = manager.list([None] * len(inputs))
    processes = []

    for idx, n in enumerate(inputs):
        p = multiprocessing.Process(target=myFunc, args=(n, idx, shared_list))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

    results = list(shared_list)
    return results


# 2:
def myFunc_process(queue,sleepTime):
    proc = current_process()
    queue.put(f"Starting process name = {proc.name}")
    time.sleep(sleepTime)  # Simulate some process work
    queue.put(f"Exiting process name = {proc.name}")


@app.get("/process")
def run_process(name1: str = Query("myFunc process"), name2: str = Query("Process-2")):
    output_queue = Queue()

    p1 = Process(name=name1, target=myFunc_process, args=(output_queue,2))
    p2 = Process(name=name2, target=myFunc_process, args=(output_queue,1))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    output_messages = []
    while not output_queue.empty():
        output_messages.append(output_queue.get())

    return output_messages


@app.get("/process_2")
def run_process(name1: str = Query("myFunc process"), name2: str = Query("Process-2")):
    output_queue = Queue()

    p1 = Process(name=name1, target=myFunc_process, args=(output_queue,2))
    p2 = Process(name=name2, target=myFunc_process, args=(output_queue,1))

    p1.start()
    p1.join()
    p2.start()
    p2.join()

    output_messages = []
    while not output_queue.empty():
        output_messages.append(output_queue.get())

    return output_messages


@app.get("/process_3")
def run_process(name1: str = Query("myFunc process"), name2: str = Query("Process-2")):
    output_queue = Queue()

    p1 = Process(name=name1, target=myFunc_process, args=(output_queue,1))
    p2 = Process(name=name2, target=myFunc_process, args=(output_queue,1))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    output_messages = []
    while not output_queue.empty():
        output_messages.append(output_queue.get())

    return output_messages



# 3:
def background_process(start, end, queue):
    queue.put("Starting background_process")
    for i in range(start, end):
        queue.put(f"---> {i}")
        time.sleep(0.5)  # ایجاد تاخیر برای مشاهده ترتیب اجرا
    queue.put("Exiting background_process")

def no_background_process(start, end, queue):
    queue.put("Starting NO_background_process")
    for i in range(start, end):
        queue.put(f"---> {i}")
        time.sleep(0.5)  # ایجاد تاخیر برای مشاهده ترتیب اجرا
    queue.put("Exiting NO_background_process")


@app.get("/run_processes_1/")
async def run_processes():
    queue = Queue()

    p1 = Process(target=no_background_process, args=(5, 10, queue))
    p2 = Process(target=no_background_process, args=(5, 10, queue))
    p3 = Process(target=background_process, args=(0, 5, queue))

    p1.start()
    p1.join()

    p2.start()
    p3.start()

    p2.join()
    p3.join()

    output = []
    while not queue.empty():
        output.append(queue.get())


@app.get("/run_processes_2/")
async def run_processes():
    queue = Queue()

    p1 = Process(target=no_background_process, args=(5, 10, queue))
    p2 = Process(target=no_background_process, args=(5, 10, queue))
    p3 = Process(target=background_process, args=(0, 5, queue))

    p1.start()
    p1.join()

    p2.start()
    p2.join()
    p3.start()
    p3.join()

    output = []
    while not queue.empty():
        output.append(queue.get())

    return output


# 4:
@app.get("/Killing_process_1/")
async def manage_process():
    process = Process()
    process_before = (str(process), process.is_alive())

    process.start()
    process_running = (str(process), process.is_alive())

    process.terminate()
    process_terminated = (str(process), process.is_alive())

    process.join()
    process_joined = (str(process), process.is_alive())

    process_exit_code = process.exitcode

    response = {
        "Process before execution": f"<Process({process.name}, initial)> {process_before[1]}",
        "Process running": f"<Process({process.name}, started)> {process_running[1]}",
        "Process terminated": f"<Process({process.name}, started)> {process_terminated[1]}",
        "Process joined": f"<Process({process.name}, stopped[SIGTERM])> {process_joined[1]}",
        "Process exit code": process_exit_code
    }
    return response


@app.get("/Killing_process_2/")
async def manage_process():
    process = Process()
    process_before = (str(process), process.is_alive())

    process.start()
    process_running = (str(process), process.is_alive())

    # process.terminate()
    # process_terminated = (str(process), process.is_alive())

    process.join()
    process_joined = (str(process), process.is_alive())

    process_exit_code = process.exitcode

    response = {
        "Process before execution": f"<Process({process.name}, initial)> {process_before[1]}",
        "Process running": f"<Process({process.name}, started)> {process_running[1]}",
        # "Process terminated": f"<Process({process.name}, started)> {process_terminated[1]}",
        "Process joined": f"<Process({process.name}, stopped[SIGTERM])> {process_joined[1]}",
        "Process exit code": process_exit_code
    }
    return response


# 5:
class MyProcess(multiprocessing.Process):
    def __init__(self, process_id, queue):
        super().__init__()
        self.process_id = process_id
        self.queue = queue

    def run(self):
        self.queue.put(f"called run method by MyProcess-{self.process_id}")

@app.get("/start_processes_1/")
async def start_processes(process_count: int = Query(default=10, ge=1, le=10)):
    queue = multiprocessing.Queue()
    processes = []

    for i in range(1, process_count + 1):
        process = MyProcess(i, queue)
        processes.append(process)
        process.start()
        process.join()

    results = []
    while not queue.empty():
        results.append(queue.get())

    return results


@app.get("/start_processes_2/")
async def start_processes(process_count: int = Query(default=10, ge=1, le=10)):
    queue = multiprocessing.Queue()
    processes = []

    for i in range(1, process_count + 1):
        process = MyProcess(i, queue)
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    results = []
    while not queue.empty():
        results.append(queue.get())

    return results


@app.get("/start_processes_3/")
async def start_processes(process_count: int = Query(default=10, ge=1, le=10)):
    queue = multiprocessing.Queue()
    processes = []

    for i in range(process_count, 0, -1):
        process = MyProcess(i, queue)
        processes.append(process)
        process.start()
        process.join()

    results = []
    while not queue.empty():
        results.append(queue.get())

    return results


# 6:
def producer(queue, log_queue, producer_id):
    for _ in range(10):
        item = random.randint(1, 300)
        queue.put((item, producer_id))
        log_queue.put(f"Process Producer : item {item} appended to queue producer-{producer_id}")
        log_queue.put(f"The size of queue is {queue.qsize()}")
        time.sleep(0.5)

def consumer(queue, log_queue, consumer_id):
    while True:
        if not queue.empty():
            item, producer_id = queue.get()
            log_queue.put(f"Process Consumer : item {item} popped from queue by consumer-{consumer_id}")
            time.sleep(1.5)
        else:
            time.sleep(0.1)  # Short sleep to avoid busy-waiting

@app.get("/start_simulation_1")
async def start_simulation():
    queue = Queue()
    log_queue = Queue()
    producers = [Process(target=producer, args=(queue, log_queue, 1))]
    consumers = [Process(target=consumer, args=(queue, log_queue, 2))]

    for p in producers:
        p.start()
    for c in consumers:
        c.start()
    for p in producers:
        p.join()

    # Wait for the queue to empty
    while not queue.empty():
        time.sleep(0.2)

    for c in consumers:
        c.terminate()
        c.join()

    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get())

    logs.append("the queue is empty")
    return logs


@app.get("/start_simulation_2")
async def start_simulation():
    queue = Queue()
    log_queue = Queue()
    producers = [Process(target=producer, args=(queue, log_queue, 1))]
    consumers = [Process(target=consumer, args=(queue, log_queue, 2))]

    for p in producers:
        p.start()
    for p in producers:
        p.join()
    for c in consumers:
        c.start()

    # Wait for the queue to empty
    while not queue.empty():
        time.sleep(0.2)

    for c in consumers:
        c.terminate()
        c.join()

    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get())

    logs.append("the queue is empty")
    return logs



def producer6_3(queue, log_queue, producer_id):
    for _ in range(10):
        item = random.randint(1, 300)
        queue.put((item, producer_id))
        log_queue.put(f"Process Producer : item {item} appended to queue producer-{producer_id}")
        log_queue.put(f"The size of queue is {queue.qsize()}")
        time.sleep(1)

def consumer6_3(queue, log_queue, consumer_id):
    while True:
        if not queue.empty():
            item, producer_id = queue.get()
            log_queue.put(f"Process Consumer : item {item} popped from queue by consumer-{consumer_id}")
            time.sleep(1)
        else:
            time.sleep(0.1)  # Short sleep to avoid busy-waiting


@app.get("/start_simulation_3")
async def start_simulation():
    queue = Queue()
    log_queue = Queue()
    producers = [Process(target=producer6_3, args=(queue, log_queue, 1))]
    consumers = [Process(target=consumer6_3, args=(queue, log_queue, 2))]

    for p in producers:
        p.start()
    for c in consumers:
        c.start()
    for p in producers:
        p.join()

    # Wait for the queue to empty
    while not queue.empty():
        time.sleep(0.2)

    for c in consumers:
        c.terminate()
        c.join()

    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get())

    logs.append("the queue is empty")
    return logs


# 7:
def test_with_barrier(barrier, process_name, log_queue):
    time.sleep(2)  # simulate some work
    barrier.wait()  # wait for other processes to reach this point
    time_now = datetime.datetime.now()
    log_queue.put(f"{process_name} - test_with_barrier ----> {time_now}")

def test_without_barrier(process_name, log_queue):
    time.sleep(1)  # simulate some work
    time_now = datetime.datetime.now()
    log_queue.put(f"{process_name} - test_without_barrier ----> {time_now}")

@app.get("/barrier_processes_1/")
async def start_processes():
    barrier = Barrier(2)  # Barrier for two processes
    log_queue = Queue()
    processes = []

    p1 = Process(target=test_without_barrier, args=('process p1', log_queue))
    p2 = Process(target=test_without_barrier, args=('process p2', log_queue))
    processes.append(p1)
    processes.append(p2)

    p3 = Process(target=test_with_barrier, args=(barrier, 'process p3', log_queue))
    p4 = Process(target=test_with_barrier, args=(barrier, 'process p4', log_queue))
    processes.append(p3)
    processes.append(p4)

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get())

    return logs


@app.get("/barrier_processes_2/")
async def start_processes():
    barrier = Barrier(2)  # Barrier for two processes
    log_queue = Queue()
    processes = []

    p1 = Process(target=test_without_barrier, args=('process p1', log_queue))
    processes.append(p1)
    p3 = Process(target=test_with_barrier, args=(barrier, 'process p3', log_queue))
    processes.append(p3)
    p2 = Process(target=test_without_barrier, args=('process p2', log_queue))
    processes.append(p2)
    p4 = Process(target=test_with_barrier, args=(barrier, 'process p4', log_queue))
    processes.append(p4)

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get())

    return logs


def test_with_barrier_3(barrier, process_name, log_queue):
    time.sleep(1)  # simulate some work
    barrier.wait()  # wait for other processes to reach this point
    time_now = datetime.datetime.now()
    log_queue.put(f"{process_name} - test_with_barrier ----> {time_now}")

def test_without_barrier_3(process_name, log_queue):
    time.sleep(2)  # simulate some work
    time_now = datetime.datetime.now()
    log_queue.put(f"{process_name} - test_without_barrier ----> {time_now}")

@app.get("/barrier_processes_3/")
async def start_processes():
    barrier = Barrier(2)  # Barrier for two processes
    log_queue = Queue()
    processes = []

    p1 = Process(target=test_without_barrier_3, args=('process p1', log_queue))
    p2 = Process(target=test_without_barrier_3, args=('process p2', log_queue))
    processes.append(p1)
    processes.append(p2)

    p3 = Process(target=test_with_barrier_3, args=(barrier, 'process p3', log_queue))
    p4 = Process(target=test_with_barrier_3, args=(barrier, 'process p4', log_queue))
    processes.append(p3)
    processes.append(p4)

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get())

    return logs


# 8:
def square(number):
    return number * number
@app.get("/process_pool_1/")
async def calculate_squares(max_number: int = Query(default=100, ge=0)):
    with Pool(processes=4) as pool:  # Use a pool of 4 processes
        result = pool.map(square, range(max_number))
    response_dict = {"Pool": result}
    return json.dumps(response_dict)


# Run the app with Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7000)