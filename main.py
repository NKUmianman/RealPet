import threading
import time

def task1():
    for _ in range(5):
        print("Task 1")
        time.sleep(1)

def task2():
    for _ in range(5):
        print("Task 2")
        time.sleep(1)

# 创建线程对象
thread1 = threading.Thread(target=task1)
thread2 = threading.Thread(target=task2)

# 启动线程
thread1.start()
thread2.start()

# 等待两个线程结束
thread1.join()
thread2.join()

print("Both threads have finished.")