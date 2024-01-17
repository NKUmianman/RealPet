import threading
import pet
import hand
import face


class SharedResource:
    def __init__(self):
        self.flag = False
        self.variable = None
        self.condition = threading.Condition()

    def set_variable(self, new_value):
        with self.condition:
            self.variable = new_value
            self.flag = True
            # 通知等待的线程，条件已经满足
            self.condition.notify()

    def get_variable(self):
        with self.condition:
            # 等待条件满足
            while self.flag is False:
                self.condition.wait()
            self.flag = False
            return self.variable


def handtask(shared_resource):
    gest = hand.GestureRecognition(signal_list=shared_resource)
    gest.run()


def facetask(shared_resource):
    face = face.FaceRecognition(signal_list=shared_resource)
    face.run()


def pettask(shared_resource):
    pet.run(signal_list=shared_resource)


if __name__ == "__main__":
    index_finger_trajectory = SharedResource()
    stop_program = SharedResource()
    # 创建线程对象
    hand_thread = threading.Thread(target=handtask, args=(
        [index_finger_trajectory, stop_program],))
    pet_thread = threading.Thread(target=pettask, args=(
        [index_finger_trajectory, stop_program],))
    face_thread = threading.Thread(target=facetask, args=([stop_program],))
    # 启动线程

    face_thread.start()
    hand_thread.start()
    pet_thread.start()

    # 等待两个线程结束
    face_thread.join()
    hand_thread.join()
    pet_thread.join()

    print("Both threads have finished.")
