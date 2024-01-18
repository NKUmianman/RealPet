import cv2
import mediapipe as mp
import time
import math

class GestureRecognition:
    def __init__(self, signal_list=None):
        self.cap = signal_list[0]
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils
        self.handLmsStyle = self.mpDraw.DrawingSpec(
            color=(0, 0, 255), thickness=5)
        self.handConStyle = self.mpDraw.DrawingSpec(
            color=(0, 255, 0), thickness=7)
        self.pTime = 0
        self.cTime = 0
        self.handsPoints = [(-1, -1)] * 42
        # self.handsPoints = [(-1,-1)] * 42
        self.index_finger_landmarks = None
        self.crawl = None
        self.signal_list = signal_list
        self.signalflag = False
    def detect_pinch_gesture(self, handLms):
        thumb_tip = handLms[4]  # 拇指指尖
        index_tip = handLms[8]  # 食指指尖

        distance = ((thumb_tip[0] - index_tip[0])**2 +
                    (thumb_tip[1] - index_tip[1])**2)**0.5

        gesture_threshold = 30  # 调整阈值以适应实际情况

        if distance < gesture_threshold:
            self.index_finger_landmarks = handLms[8]  # 保存食指关键点
            return True
        else:
            self.index_finger_landmarks = None  # 重置食指关键点
            return False

    def track_index_finger_movement(self, handLms):
        if self.index_finger_landmarks:
            current_index_tip = handLms[8]  # 当前食指指尖的关键点
            # 计算移动向量
            movement_vector = (
                current_index_tip[0] - self.index_finger_landmarks[0],
                current_index_tip[1] - self.index_finger_landmarks[1]
            )

            # 处理移动向量（例如，打印或在你的应用程序中使用它）
            print("食指移动：", movement_vector)
            if self.signal_list:
                self.signal_list[2].set_variable(self.crawl)
                self.signalflag = True
            return movement_vector
        if self.signalflag == True:
            if self.signal_list:
                self.signal_list[2].set_variable(None)
                self.signalflag = False
        return None

    def detect_touch_gesture(self, handLms):
        root = handLms[0]  # 手掌根部
        thumb_tip = handLms[4]  # 拇指指尖
        middle_tip = handLms[12]  # 中指指尖
        ring_tip = handLms[16]  # 无名指指尖
        pinky_tip = handLms[20]  # 小指指尖

        distances = [((tip[0] - root[0])**2 +
                      (tip[1] - root[1])**2)**0.5 for tip in (thumb_tip, middle_tip, ring_tip, pinky_tip)]

        # 设置手势的阈值，根据需要进行调整
        fingers_threshold = 70  # 其他指头并拢的距离阈值

        # 食指指尖距离摄像头够近，并且其他指头都在一定距离内
        if distances[0] < fingers_threshold and \
                distances[1] < fingers_threshold and \
                distances[2] < fingers_threshold and \
                distances[3] < fingers_threshold:
            self.signal_list[3].set_variable(True)
            return True
        else:
            self.signal_list[3].set_variable(False)
            return False
    
    def detect_shooting_gesture(self, handLms):
        thumb_tip = handLms[4]   # 拇指指尖
        thumb_mid = handLms[3]   # 拇指第二关节
        index_finger_tip = handLms[8]   # 食指指尖
        index_finger_base = handLms[5]   # 食指第二关节

        # 判断拇指朝上
        thumb_vector = (thumb_tip[0] - thumb_mid[0], thumb_tip[1] - thumb_mid[1])
        thumb_angle = math.degrees(math.atan2(thumb_vector[1], thumb_vector[0]))  # 拇指向量与y轴的夹角
        thumb_up = (thumb_angle > -90 and thumb_angle < -70)

        # 判断食指指向屏幕,因为没有z轴，用的是食指到食指基部的距离是否超过阈值判断，如果这个距离比较小就是近似重合，理解成食指指向屏幕，但也不太严谨
        index_finger_distance_threshold = 40  # 食指到食指基部的距离阈值

        index_finger_distance = math.sqrt(
            (index_finger_tip[0] - index_finger_base[0]) ** 2 + (index_finger_tip[1] - index_finger_base[1]) ** 2
        )

        index_finger_pointing = index_finger_distance <= index_finger_distance_threshold
        # print("thumb_angle",thumb_angle)
        # print("index_finger_distance",index_finger_distance)

        distance = ((thumb_tip[0] - index_finger_tip[0])**2 +
                    (thumb_tip[1] - index_finger_tip[1])**2)**0.5
        
        if thumb_up and index_finger_pointing and distance>30:
            self.signal_list[4].set_variable(True)
            return True   # 检测到开枪手势
        else:
            self.signal_list[4].set_variable(False)
            return False   # 未检测到开枪手势
    def run(self):
        while True:
            ret, img = self.cap.read()
            handsPoints = [(-1, -1)] * 21
            img = cv2.flip(img, 1)  # 1 for horizontal flip
            if ret:
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                result = self.hands.process(imgRGB)
                # print(result.multi_hand_landmarks)
                imgHeight = img.shape[0]
                imgWidth = img.shape[1]

                if result.multi_hand_landmarks:
                    # print("集合",(result.multi_hand_landmarks))
                    # print((result.multi_handedness[0].classification[0].label))
                    # print("左右手", result.multi_handedness)
                    # print("multi_hand_landmarks",result.multi_hand_landmarks)
                    if (len(result.multi_hand_landmarks) == 1):
                        handsPoints = [(-1, -1)] * 21
                        for i, handLms in enumerate(result.multi_hand_landmarks):
                            self.mpDraw.draw_landmarks(
                                img, handLms, self.mpHands.HAND_CONNECTIONS, self.handLmsStyle, self.handConStyle)
                            for j, lm in enumerate(handLms.landmark):
                                xpos = int(lm.x * imgWidth)
                                ypos = int(lm.y * imgHeight)
                                # handsPoints.append((xpos, ypos))
                                handsPoints[j] = (xpos, ypos)
                    elif (len(result.multi_hand_landmarks) == 2):
                        handsPoints = [(-1, -1)] * 42
                        for i, handLms in enumerate(result.multi_hand_landmarks):
                            self.mpDraw.draw_landmarks(
                                img, handLms, self.mpHands.HAND_CONNECTIONS, self.handLmsStyle, self.handConStyle)
                            for j, lm in enumerate(handLms.landmark):
                                xpos = int(lm.x * imgWidth)
                                ypos = int(lm.y * imgHeight)
                                # handsPoints.append((xpos, ypos))
                                if (result.multi_handedness[i].classification[0].label == 'Right'):
                                    # print("LEFT")
                                    handsPoints[j] = (xpos, ypos)
                                elif (result.multi_handedness[i].classification[0].label == 'Left'):
                                    # print("Right")
                                    handsPoints[j+21] = (xpos, ypos)
                        # self.crawl=self.track_index_finger_movement(handsPoints)
                    # print('handsPoints:', handsPoints)
                    # print(len(handsPoints))

                    # if self.detect_pinch_gesture(handsPoints):
                    # cv2.putText(img, "Pinch Gesture Detected", (30, 100),
                    # cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    # if self.signalfuctin and self.crawl!=(0,0):
                    #     self.signalfuctin(self.crawl)
                    for handLms in result.multi_hand_landmarks:
                        self.mpDraw.draw_landmarks(
                            img, handLms, self.mpHands.HAND_CONNECTIONS, self.handLmsStyle, self.handConStyle)
                        handsPoints = []
                        for i, lm in enumerate(handLms.landmark):
                            xpos = int(lm.x * imgWidth)
                            ypos = int(lm.y * imgHeight)
                            handsPoints.append((xpos, ypos))
                            cv2.putText(img, str(i), (xpos-25, ypos+5),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 2)
                            # if i==4:
                            #     cv2.circle(img, (xpos, ypos), 10, (0,0,255), cv2.FILLED)
                            # print(i, xpos, ypos)
                        self.crawl = self.track_index_finger_movement(
                            handsPoints)

                        if self.detect_pinch_gesture(handsPoints):
                            cv2.putText(img, "Pinch Gesture Detected", (30, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

                        if self.detect_touch_gesture(handsPoints):
                            cv2.putText(img, "Touch Gesture Detected", (30, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                        if self.detect_shooting_gesture(handsPoints):
                            cv2.putText(img, "Shoot Gesture Detected", (30, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                        # if self.signal_list and self.crawl!=(0,0):
                        #     self.signal_list(self.crawl)

                self.cTime = time.time()
                fps = 1/(self.cTime-self.pTime)
                self.pTime = self.cTime
                cv2.putText(img, f"fps: {int(fps)}", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                cv2.imshow('img', img)
            # print("handsPoints:",handsPoints)
            if cv2.waitKey(1) == ord('q'):
                break
            if self.signal_list:
                # 设置非信号函数非阻塞检查
                self.signal_list[1].flag = True
                state = self.signal_list[1].get_variable()
                # print(state)
                if state == True:
                    print("hand线程退出")
                    break


if __name__ == "__main__":
    gest = GestureRecognition()
    gest.run()
