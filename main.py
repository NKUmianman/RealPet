import threading
import pet
import hand
import face
import cv2
from shareResource import SharedResource


def handtask(shared_resource):
    gest = hand.GestureRecognition(signal_list=shared_resource)
    gest.run()


def facetask(shared_resource):
    feature = face.FaceRecognition(signal_list=shared_resource)
    feature.run()


def pettask(shared_resource):
    pet.run(signal_list=shared_resource)


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    face_feature = SharedResource()
    pinch = SharedResource()
    bodytouch = SharedResource()
    headtouch = SharedResource()
    shoot = SharedResource()
    stop_program = SharedResource()
    # 创建线程对象
    hand_thread = threading.Thread(target=handtask, args=(
        [cap, stop_program, pinch, bodytouch, headtouch, shoot],))
    face_thread = threading.Thread(
        target=facetask, args=([cap, stop_program, face_feature],))
    pet_thread = threading.Thread(target=pettask, args=(
        [stop_program, pinch, bodytouch, headtouch, face_feature, shoot],))
    # 启动线程

    face_thread.start()
    hand_thread.start()
    pet_thread.start()

    # 等待两个线程结束
    face_thread.join()
    hand_thread.join()
    pet_thread.join()

    print("Both threads have finished.")
