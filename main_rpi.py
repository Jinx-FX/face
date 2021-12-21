# -*- coding:utf-8 -*
from chj.ogl import light
from chj.ogl.objloader import CHJ_tiny_obj, OBJ
from chj.ogl import *
import os
import sys
import cv2 as cv
from deepface import DeepFace
import time

os.chdir(os.path.split(os.path.realpath(sys.argv[0]))[0])

model_bin = "/home/pi/face_ar/face_detector/opencv_face_detector_uint8.pb"
config_text = "/home/pi/face_ar/face_detector/opencv_face_detector.pbtxt"

fidr = "models_obj/"
fobj = "14_sadness.obj"
fobj_pkl = "chj/obj.pkl"


class param(object):
    pass


def run_ogl(fidr, fobj_pkl, fobj):
    # ugly： 第一次加载写 1==1， 如果仍用同一个模型，第二次写 1 == 0
    if 1 == 1:
        obj = OBJ(fidr, fobj, swapyz=False)
        obj.create_bbox()

        with open(fobj_pkl, 'wb') as f:  # open file with write-mode
            pickle.dump(obj, f)  # picklestring = pickle.dumps(summer)
    else:
        with open(fobj_pkl, 'rb') as f:
            obj = pickle.load(f)

    param.obj = obj
    param.sel_pos = False

    pygame.init()
    viewport = (200, 200)
    param.viewport = viewport
    screen = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)
    param.screen = screen

    light.setup_lighting()
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 1000, 0))  # 指的是光的朝向

    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)  # most obj files expect to be smooth-shaded

    obj.create_gl_list()

    clock = pygame.time.Clock()

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    cam = light.camera
    cam.Ortho.bbox[:] = cam.Ortho.bbox * 13
    cam.Ortho.nf[:] = cam.Ortho.nf * 200
    # glOrtho(*cam.Ortho.params)
    # gluPerspective(fovy=60, aspect=1, zNear=0.1, zFar=1000)
    gluPerspective(60, 1, 0.1, 10000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # gluLookAt( eyex=0, eyey=0, eyez=100, centerx=0, centery=0, centerz=0, upx=0, upy=1, upz=0)
    gluLookAt(0, 0, 800, 0, 0, 0, 0, 1, 0)

    rx, ry = (0, 0)
    tx, ty = (0, 0)
    zpos = 5
    rotate = move = False

    # 开始渲染
    clock.tick(30)
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # elif e.key == pygame.K_s:

            elif e.key == pygame.K_4:
                param.sel_pos = not param.sel_pos

        elif e.type == MOUSEBUTTONDOWN:

            pressed_array = pygame.mouse.get_pressed()
            if pressed_array[0]:  # 左键被按下
                if param.sel_pos:
                    pos = pygame.mouse.get_pos()  # 获得鼠标位置
                    pos_get_pos3d_show(pos)

            if e.button == 4:
                zpos = max(1, zpos - 1)
            elif e.button == 5:
                zpos += 1
            elif e.button == 1:
                rotate = True
            elif e.button == 3:
                move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1:
                rotate = False
            elif e.button == 3:
                move = False
        elif e.type == MOUSEMOTION:
            # p(e.rel)
            i, j = e.rel
            if rotate:
                rx -= i
                ry -= j
            if move:
                tx += i
                ty -= j

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    # RENDER OBJECT
    glTranslate(tx / 20., ty / 20., - zpos)
    glRotate(ry / 5, 1, 0, 0)
    glRotate(rx / 5, 0, 1, 0)

    # glRotate(180, 0, 1, 0)  # 这个是通过观察得到的
    s = [2 / obj.bbox_half_r] * 3
    glScale(*s)

    t = -obj.bbox_center
    glTranslate(*t)

    glCallList(obj.gl_list)
    if hasattr(param, 'pos3d') and param.sel_pos:
        draw_pos(param.pos3d)

    pygame.display.flip()
    #  time.sleep(3)
    #  pygame.quit()
    #  break


def pos_get_pos3d(pos):
    x = pos[0]
    y = param.viewport[1] - pos[1]
    # 这个是说读出一个矩形 左下角， 长宽
    z = glReadPixels(x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)  # 获得的是 NDC中的坐标

    # 获得必要的矩阵
    # 4 16 16
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)

    # p(viewport)
    # p(modelview)
    # p(projection)
    xyz = gluUnProject(x, y, z, modelview, projection, viewport)
    return xyz


def pos_get_pos3d_show(pos):
    # p(pos)
    pos3d = pos_get_pos3d(pos)
    param.pos3d = pos3d

    p("pos3d", pos3d)


def draw_pos(pos3d, size=10, color=[0, 1, 0]):
    glPointSize(size)
    glBegin(GL_POINTS)

    glColor3f(*color)
    glVertex3f(*pos3d)

    glEnd()
    glColor3f(1, 1, 1)


if __name__ == "__main__":

    # load tensorflow model
    net = cv.dnn.readNetFromTensorflow(model_bin, config=config_text)
    capture = cv.VideoCapture(0)
    #  capture.set(5, 20000)
    #  capture.set(7, 100000000)
    wCam, hCam = 640, 480
    capture.set(3, wCam)
    capture.set(4, hCam)

    # 人脸检测
    while 1:
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

        if emotion == "angry":
            fobj = "4_anger.obj"
        elif emotion == "fear":
            fobj = "13_lip_funneler.obj"
        elif emotion == "sad":
            fobj = "14_sadness.obj"
        elif emotion == "disgust":
            fobj = "18_eye_closed.obj "
        elif emotion == "happy":
            fobj = "2_smile.obj"
        elif emotion == "surprise":
            fobj = "3_mouth_stretch.obj"
        else:
            fobj = "1_neutral.obj"

        run_ogl(fidr, fobj_pkl, fobj)

        if cv.waitKey(1) == 27:
            break

    cv.destroyAllWindows()
