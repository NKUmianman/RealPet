import onnxruntime
import time
import numpy as np
import cv2
import mediapipe as mp

from PIL import Image, ImageDraw, ImageFont


class FaceRecognition:
    def __init__(self, signal_list=None):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        # 视频输入，如果需要摄像头，请改成数字0，并修改下面的break为continue
        self.cap = signal_list[0]
        self.ort_session = onnxruntime.InferenceSession(
            "cpu.onnx", providers=['CPUExecutionProvider'])
        self.list_attr = np.array(["不明显的胡子", "拱形眉毛", "有吸引力的", "眼袋", "秃头", "刘海", "大嘴唇", "大鼻子", "黑发", "金发",
                                   "模糊的", "棕发", "浓眉", "圆胖", "双下巴", "眼镜", "山羊胡子", "灰白发", "浓妆", "高高的颧骨",
                                   "男生", "嘴巴张开", "胡子", "眯眯眼", "没有胡子", "鹅蛋脸", "白皮肤", "尖鼻子", "后退的发际线", "红润脸颊",
                                   "鬓角", "微笑", "直发", "卷发", "耳环", "帽子", "口红", "项链", "领带", "年轻"])  # 中文属性

        self.signal_list = signal_list
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 获取视频宽度
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 获取视频高度
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)  # 获取视频FPS，如果是实时摄像头请手动设定帧数

    def cv2_preprocess(self, img):  # numpy预处理和torch处理一样
        img = cv2.resize(img, (128, 128), interpolation=cv2.INTER_NEAREST)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mean = [0.5, 0.5, 0.5]  # 一定要是3个通道，不能直接减0.5
        std = [0.5, 0.5, 0.5]
        img = ((img / 255.0 - mean) / std)
        img = img.transpose((2, 0, 1))  # hwc变为chw
        img = np.expand_dims(img, axis=0)  # 3维到4维
        img = np.ascontiguousarray(img, dtype=np.float32)  # 转换浮点型
        return img

    def sigmoid_array(self, x):  # sigmoid函数手动设定
        return 1 / (1 + np.exp(-x))

    def result_inference(self, input_array):  # 推理环节
        ort_inputs = {self.ort_session.get_inputs()[0].name: input_array}
        ort_outs = self.ort_session.run(None, ort_inputs)
        possibility = self.sigmoid_array(ort_outs[0]) > 0.5
        result = self.list_attr[possibility[0]]
        return result

    def run(self):
        with self.mp_face_detection.FaceDetection(
                model_selection=1, min_detection_confidence=0.5) as face_detection:
            # 人脸识别，1为通用模型，0为近距离模型
            while self.cap.isOpened():
                a1 = time.time()
                success, image = self.cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue
                image.flags.writeable = False  # 据说这样写可以加速人脸识别推理
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_detection.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                image2 = image.copy()  # copy复制，因为cv2会直接覆盖原有数组
                if results.detections:
                    for detection in results.detections:
                        self.mp_drawing.draw_detection(image, detection)
                        image_rows, image_cols, _ = image.shape
                        location = detection.location_data.relative_bounding_box  # 获取人脸位置
                        start_point = self.mp_drawing._normalized_to_pixel_coordinates(
                            location.xmin, location.ymin, image_cols, image_rows)  # 获取人脸左上角的点
                        end_point = self.mp_drawing._normalized_to_pixel_coordinates(
                            location.xmin + location.width, location.ymin + location.height, image_cols, image_rows)  # 获取右下角的点
                        if start_point == None or end_point == None:
                            break
                        x1, y1 = start_point  # 左上点坐标
                        x2, y2 = end_point  # 右下点坐标
                        # 为了营造相似环境，把左上角和右上角的点连线囊括的区域扩大提高准确度
                        img_infer = image2[y1-70:y2, x1-50:x2+50].copy()
                        img_infer = self.cv2_preprocess(img_infer)
                        result = self.result_inference(img_infer)
                        self.signal_list[2].set_variable(result)
                        # print(result)
                        # cv2.imshow('test', img_infer)
                        # if cv2.waitKey(5) & 0xFF == 27:
                        #   break
                        for i in range(0, len(result)):
                            # 将OpenCV图像从BGR转换为RGB
                            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            image = Image.fromarray(image)
                            draw = ImageDraw.Draw(image)
                            font = ImageFont.truetype(
                                "simhei.ttf", 30, encoding="utf-8")
                            draw.text((x1, y1+i*40),
                                      result[i], (255, 255, 255), font=font)
                            image = cv2.cvtColor(
                                np.array(image), cv2.COLOR_RGB2BGR)
                            # cv2.imshow('Camera', image)
                            # cv2.waitKey(1)
                    a2 = time.time()
                # cv2.imshow('Camera', image)
                cv2.waitKey(2)
                if self.signal_list:
                    # 设置非信号函数非阻塞检查
                    self.signal_list[1].flag = True
                    state = self.signal_list[1].get_variable()
                    # print(state)
                    if state == True:
                        print("face线程退出")
                        break

                # out.write(image)
                # print(f'one pic time is {a2 - a1} s')
