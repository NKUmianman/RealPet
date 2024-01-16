import threading
import pet
import hand
import face
class SharedResource:
    def __init__(self):
        self.flag=False
        self.variable = None
        self.condition = threading.Condition()

    def set_variable(self, new_value):
        with self.condition:
            self.variable = new_value
            self.flag=True
            # 通知等待的线程，条件已经满足
            self.condition.notify()

    def get_variable(self):
        with self.condition:
            # 等待条件满足
            while self.flag is False:
                self.condition.wait()
            self.flag=False
            return self.variable

def handtask(shared_resource):
    gest=hand.GestureRecognition(signalfuctin=shared_resource)
    gest.run()

def pettask(shared_resource):
    pet.run(signalfuctin=shared_resource)

def facetask(shared_resource):
    face.run(signalfuctin=shared_resource)
    

if __name__=="__main__":
    index_finger_trajectory=SharedResource()
    sample=SharedResource()
    # 创建线程对象
    thread1 = threading.Thread(target=handtask,args=([index_finger_trajectory,sample],))
    thread2 = threading.Thread(target=pettask,args=([index_finger_trajectory,sample],))
    thread3 = threading.Thread(target=facetask,args=([sample],))
    # 启动线程
    thread1.start()
    thread2.start()

    # 等待两个线程结束
    thread1.join()
    thread2.join()

    print("Both threads have finished.")