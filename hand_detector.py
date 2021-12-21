# -*- coding:utf-8 -*
from chj.ogl import light
from chj.ogl.objloader import CHJ_tiny_obj, OBJ
from chj.ogl import *
import os
import sys
import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import numpy as np
import cvzone
import time

os.chdir(os.path.split(os.path.realpath(sys.argv[0]))[0])

fidr = "models_obj/"
fobj = "3_mouth_stretch.obj"
fobj_pkl = "chj/obj.pkl"

# Webcam
cap = cv2.VideoCapture(0)
#  cap.set(3, 1280)
#  cap.set(4, 720)

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Find Function
# x is the raw distance y is the value in cm
x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(x, y, 2)  # y = Ax^2 + Bx + C


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
    # 改变窗口大小
    viewport = (700, 700)
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
    #gluLookAt( eyex=0, eyey=0, eyez=100, centerx=0, centery=0, centerz=0, upx=0, upy=1, upz=0)
    gluLookAt(0, 0, 800, 0, 0, 0, 0, 1, 0)

    rx, ry = (0, 0)
    tx, ty = (0, 0)
    zpos = 5
    rotate = move = False

    # 开始渲染
    while 1:
        success, img = cap.read()
        hands = detector.findHands(img, draw=False)

        if hands:
            lmList = hands[0]['lmList']
            x, y, w, h = hands[0]['bbox']
            x1, y1 = lmList[5]
            x2, y2 = lmList[17]

            distance = int(math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2))
            A, B, C = coff
            distanceCM = A * distance ** 2 + B * distance + C

            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 3)
            cvzone.putTextRect(img, f'{int(distanceCM)} cm', (x+5, y-10))
            # 放大
            if distanceCM < 50:
                zpos = max(1, zpos - 1)
            # 缩小
            elif distanceCM > 70:
                zpos = zpos + 1

        if cv2.waitKey(1) == 27:
            break

        cv2.imshow("Image", img)
        cv2.waitKey(1)

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
                # 控制放大缩小
                if e.button == 4:
                    zpos = max(1, zpos - 1)
                elif e.button == 5:
                    zpos += 1

                elif e.button == 1:
                    rotate = True
                elif e.button == 3:
                    move = True
            # 使鼠标按下才进行相应操作
            elif e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    rotate = False
                elif e.button == 3:
                    move = False
            # 旋转
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
    run_ogl(fidr, fobj_pkl, fobj)
