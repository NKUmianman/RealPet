import cv2
import mediapipe as mp
import time

class GestureRecognition():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpDraw = mp.solutions.drawing_utils
        self.handLmsStyle = self.mpDraw.DrawingSpec(color=(0, 0, 255), thickness=5)
        self.handConStyle = self.mpDraw.DrawingSpec(color=(0, 255, 0), thickness=7)
        self.pTime = 0
        self.cTime = 0
        self.handsPoints = []
    def detect_pinch_gesture(self,handLms):
        thumb_tip = handLms[4]  # 拇指指尖
        index_tip = handLms[8]  # 食指指尖

        distance = ((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)**0.5

        gesture_threshold = 50  # 调整阈值以适应实际情况

        if distance < gesture_threshold:
            return True
        else:
            return False
    
    def run(self):
        while True:
            ret, img = self.cap.read()
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
                        handLmsPoints = []
                        for i, lm in enumerate(handLms.landmark):
                            xpos = int(lm.x * imgWidth)
                            ypos = int(lm.y * imgHeight)
                            handLmsPoints.append((xpos, ypos))
                            # cv2.putText(img, str(i), (xpos-25, ypos+5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 2)
                            # if i==4:
                            #     cv2.circle(img, (xpos, ypos), 10, (0,0,255), cv2.FILLED)
                            # print(i, xpos, ypos)
                        if self.detect_pinch_gesture(handLmsPoints):
                            cv2.putText(img, "Pinch Gesture Detected", (30, 100),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                cTime = time.time()
                fps = 1/(self.cTime-self.pTime)
                self.pTime = self.cTime
                cv2.putText(img, f"fps: {int(fps)}", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

                cv2.imshow('img', img)

            if cv2.waitKey(1) == ord('q'):
                break
if __name__=="__main__":
    gest=GestureRecognition()
    gest.run()