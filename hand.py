import cv2
import mediapipe as mp
import time


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
        self.handsPoints = []
        self.index_finger_landmarks = None
        self.index_finger_trajectory = None
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
                self.signal_list[1].set_variable(self.index_finger_trajectory)
                self.signalflag = True
            return movement_vector
        if self.signalflag == True:
            if self.signal_list:
                self.signal_list[1].set_variable(None)
                self.signalflag = False
        return None

    def run(self):
        while True:
            ret, img = self.cap.read()
            img = cv2.flip(img, 1)  # 1 for horizontal flip
            if ret:
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                result = self.hands.process(imgRGB)
                # print(result.multi_hand_landmarks)
                imgHeight = img.shape[0]
                imgWidth = img.shape[1]

                if result.multi_hand_landmarks:
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
                        self.index_finger_trajectory = self.track_index_finger_movement(
                            handsPoints)

                        if self.detect_pinch_gesture(handsPoints):
                            cv2.putText(img, "Pinch Gesture Detected", (30, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                        # if self.signal_list and self.index_finger_trajectory!=(0,0):
                        #     self.signal_list(self.index_finger_trajectory)

                self.cTime = time.time()
                fps = 1/(self.cTime-self.pTime)
                self.pTime = self.cTime
                cv2.putText(img, f"fps: {int(fps)}", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                cv2.imshow('img', img)

            if cv2.waitKey(1) == ord('q'):
                break
            if self.signal_list:
                # 设置非信号函数非阻塞检查
                self.signal_list[2].flag = True
                state = self.signal_list[2].get_variable()
                # print(state)
                if state == True:
                    print("hand线程退出")
                    break


if __name__ == "__main__":
    gest = GestureRecognition()
    gest.run()
