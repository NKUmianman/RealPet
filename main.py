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

if __name__=="__main__":
    index_finger_trajectory=SharedResource()
    stop_program=SharedResource()
    # 创建线程对象
    thread1 = threading.Thread(target=handtask,args=([index_finger_trajectory,stop_program],))
    thread2 = threading.Thread(target=pettask,args=([index_finger_trajectory,stop_program],))
    thread3 = threading.Thread(target=facetask,args=([stop_program],))
    # 启动线程

    face_thread.start()
    hand_thread.start()
    pet_thread.start()

    # 等待两个线程结束
    face_thread.join()
    hand_thread.join()
    pet_thread.join()

    print("Both threads have finished.")
