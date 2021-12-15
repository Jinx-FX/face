import cv2 as cv
from deepface import DeepFace

model_bin = "/home/july/project/AR/face/face_detector/opencv_face_detector_uint8.pb"
config_text = "/home/july/project/AR/face/face_detector/opencv_face_detector.pbtxt"


def video_detection():
    # load tensorflow model
    net = cv.dnn.readNetFromTensorflow(model_bin, config=config_text)
    capture = cv.VideoCapture(0)
    #  wCam, hCam = 70, 40
    #  capture.set(3, wCam)
    #  capture.set(4, hCam)

    # 人脸检测
    while capture.isOpened:
        e1 = cv.getTickCount()
        ret, frame = capture.read()

        if ret is not True:
            break
        h, w, c = frame.shape
        blobImage = cv.dnn.blobFromImage(
            frame, 1.0, (300, 300), (104.0, 177.0, 123.0), False, False)
        net.setInput(blobImage)
        cvOut = net.forward()

        # 绘制检测矩形
        for detection in cvOut[0, 0, :, :]:
            score = float(detection[2])
            objIndex = int(detection[1])
            if score > 0.5:
                left = detection[3]*w
                top = detection[4]*h
                right = detection[5]*w
                bottom = detection[6]*h

                # 绘制
                cv.rectangle(frame, (int(left), int(top)), (int(
                    right), int(bottom)), (255, 0, 0), thickness=2)
                cv.putText(frame, "score:%.2f" % score, (int(left), int(
                    top)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        try:
            pred = DeepFace.analyze(frame, actions=['emotion'])
        except Exception:
            emotion = "I can't understand you, sorry"
        else:
            emotion = pred['dominant_emotion']

        cv.putText(frame, emotion, (10, 50),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        cv.imshow('face-detection-demo', frame)
        c = cv.waitKey(1)
        if c == 27:
            break

    cv.destroyAllWindows()


if __name__ == "__main__":
    video_detection()
