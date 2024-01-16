import threading
import time

class SharedResource:
    def __init__(self):
        self.variable = None
        self.condition = threading.Condition()

    def set_variable(self, new_value):
        with self.condition:
            self.variable = new_value
            # 通知等待的线程，条件已经满足
            self.condition.notify()

    def get_variable(self):
        with self.condition:
            # 等待条件满足
            while self.variable is None:
                self.condition.wait()
            return self.variable

def thread1(shared_resource):
    for i in range(5):
        time.sleep(1)
        shared_resource.set_variable(i)
        print(f"Thread 1 set variable to {i}")

def thread2(shared_resource):
    while True:
        time.sleep(1)
        value = shared_resource.get_variable()
        print(f"Thread 2 got variable: {value}")

if __name__ == "__main__":
    shared_resource = SharedResource()

    t1 = threading.Thread(target=thread1, args=(shared_resource,))
    t2 = threading.Thread(target=thread2, args=(shared_resource,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()
