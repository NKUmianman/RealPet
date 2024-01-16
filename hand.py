import cv2
import mediapipe as mp
import time

class GestureRecognition:
    def __init__(self,signalfuctin=None):
        self.cap = cv2.VideoCapture(0)
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils
        self.handLmsStyle = self.mpDraw.DrawingSpec(color=(0, 0, 255), thickness=5)
        self.handConStyle = self.mpDraw.DrawingSpec(color=(0, 255, 0), thickness=7)
        self.pTime = 0
        self.cTime = 0
        self.handsPoints = [(-1,-1)] * 42
        # self.handsPoints = [(-1,-1)] * 42
        self.index_finger_landmarks = None
        self.index_finger_trajectory=None
        self.signalfuctin=signalfuctin

    def detect_pinch_gesture(self,handLms):
        thumb_tip = handLms[4]  # 拇指指尖
        index_tip = handLms[8]  # 食指指尖

        distance = ((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)**0.5

        gesture_threshold = 50  # 调整阈值以适应实际情况

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
            self.signalfuctin(self.index_finger_trajectory)
            return movement_vector
        return (0,0)
    
    def run(self):
        while True:
            ret, img = self.cap.read()
            handsPoints  = [(-1,-1)] * 42
            if ret:
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                result = self.hands.process(imgRGB)
                # print(result.multi_hand_landmarks)
                imgHeight = img.shape[0]
                imgWidth = img.shape[1]
                if result.multi_hand_landmarks:
                    # print("集合",(result.multi_hand_landmarks))
                    # print((result.multi_handedness[0].classification[0].label))
                    # print("左右手",result.multi_handedness)
                    # print("multi_hand_landmarks",result.multi_hand_landmarks)
                    for i,handLms in enumerate(result.multi_hand_landmarks):
                        self.mpDraw.draw_landmarks(
                            img, handLms, self.mpHands.HAND_CONNECTIONS, self.handLmsStyle, self.handConStyle)
                        for j, lm in enumerate(handLms.landmark):
                            xpos = int(lm.x * imgWidth)
                            ypos = int(lm.y * imgHeight)
                            # handsPoints.append((xpos, ypos))
                            if(result.multi_handedness[i].classification[0].label == 'Right'):
                                handsPoints[j]=(xpos, ypos)
                            elif(result.multi_handedness[i].classification[0].label == 'Left'):
                                handsPoints[j+21]=(xpos, ypos)
                        
                        # self.index_finger_trajectory=self.track_index_finger_movement(handsPoints)
                    print('handsPoints:',handsPoints)
                    print(len(handsPoints))
            
                        # if self.detect_pinch_gesture(handsPoints):
                            # cv2.putText(img, "Pinch Gesture Detected", (30, 100),
                                        # cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                        # if self.signalfuctin and self.index_finger_trajectory!=(0,0):
                        #     self.signalfuctin(self.index_finger_trajectory)
                self.cTime = time.time()
                fps = 1/(self.cTime-self.pTime)
                self.pTime = self.cTime
                cv2.putText(img, f"fps: {int(fps)}", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

                cv2.imshow('img', img)
            print("handsPoints:",handsPoints)
            if cv2.waitKey(1) == ord('q'):
                break

if __name__=="__main__":
    gest=GestureRecognition()
    gest.run()