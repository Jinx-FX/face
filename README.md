
<!-- TOC Marked -->

+ [基于三维人脸数据的AR互动平台开发](#基于三维人脸数据的ar互动平台开发)
    * [我使用的系统 `Manjaro`](#我使用的系统-`manjaro`)
        - [Requirements](#requirements)
        - [运行示例](#运行示例)
    * [人脸表情实时识别](#人脸表情实时识别)
        - [Demo](#demo)
    * [3D模型加载](#3d模型加载)
        - [Demo](#demo)
    * [手掌交互](#手掌交互)
        - [Demo](#demo)
    * [可能遇到的问题：](#可能遇到的问题：)
+ [参考与感谢](#参考与感谢)

<!-- /TOC -->
# 基于三维人脸数据的AR互动平台开发

根据已有的三维人脸数据，开发一款基于普通投影仪或显示器和普通相机的人机交互系统，要求
1. 实现三维人脸的渲染和显示；
2. 能识别相机前实时采集的面部表情，比如大笑、沮丧等；能根据面部表情变化对应调整三维人脸数据；
3. 手掌交互,检查手掌到摄像头的距离对三维模型进行放大或缩小

## 我使用的系统 `Manjaro`

![manjaro](/readme_use/system_show.png)

### Requirements

```sh
pip install pygame PyOpenGL PyOpenGL_accelerate
pip install deepface tensorflow
pip install numpy
pip install opencv-python
pip install mediapipe cvzone
```

### 运行示例

```sh
python3 main.py
```

## 人脸表情实时识别

by deepface

### Demo

1. face_detector.py

![](/readme_use/face_detector_test.png)

## 3D模型加载

by pygame pyopengl

使用`pyopengl`进行3d模型的加载

### Demo

1. obj_show.py

![](/readme_use/obj_show_test.png)

2. light.py 用于设置光照和相机

3. objloader.py 用于加载模型和纹理

You can use mouse to move, rotate and scale it. And you may set lighting for a better viewing. You need to be familiar with opengl.

(鼠标移动，自行设置光照，具体可以看代码)

See the code to learn more. (eg. I use `pickle` to accelerate loading, obj.pkl 即缓存文件)

## 手掌交互

by mediapipe cvzone

根据手掌到摄像头的距离使三维人脸模型放大或缩小

原理：根据手掌某两点的距离与实际到摄像头的距离拟合一个关于x和y的函数,
再根据这个函数去判断距离

### Demo

1. hand_detector.py

### 实现环境配置

1. pip 换源(也可以不换),然后依次安装上面的python库

2. 配置opengl的环境
```sh
sudo apt-get install build-essential # 基本编译环境
sudo apt-get install libgl1-mesa-dev # opengl library
sudo apt-get install libglu1-mesa-dev # opengl utilities
sudo apt-get install libglut-dev # opengl utilities toolkit
```

需要注意的是:第四步可能会有报错,像如下
```sh
Reading package lists… Done
Building dependency tree
Reading state information… Done
E: Unable to locate package libglut-dev
```

这时将上述命令改为`sudo apt-get install freeglut3-dev`即可.


## 可能遇到的问题：

1. pyopengl运行不成功,error可能像这样
```
libGL error: MESA-LOADER: failed to open iris: /home/hosameldin/miniforge3/envs/robenv/bin/../lib/libstdc++.so.6: version `GLIBCXX_3.4.29' not found (required by /usr/lib/dri/iris_dri.so) (search paths /usr/lib/dri)
libGL error: failed to load driver: iris
libGL error: MESA-LOADER: failed to open iris: /home/hosameldin/miniforge3/envs/robenv/bin/../lib/libstdc++.so.6: version `GLIBCXX_3.4.29' not found (required by /usr/lib/dri/iris_dri.so) (search paths /usr/lib/dri)
libGL error: failed to load driver: iris
```

> 解决：[参考链接](https://github.com/conda-forge/gazebo-feedstock/issues/81) 
>
> 在 `*shrc` 配置文件中加入
> ```sh
> export LD_PRELOAD=/usr/lib/libstdc++.so.6 pyopengl
> ```

> 如果你用的是`win`， 参考这个[链接](https://blog.csdn.net/qq_45362415/article/details/104531503)


# 参考与感谢 
- [changhongjian](https://github.com/changhongjian/pygame-show-obj)
- [opencv_ai](https://gitee.com/opencv_ai/opencv_tutorial_data?_from=gitee_search)
- [OBJFileLoader](https://www.pygame.org/wiki/OBJFileLoader)
- [BXT-AR-For-Python](https://gitee.com/791529351/BXT-AR4Python)
- [facescape](https://facescape.nju.edu.cn/)
- [Fata-DL](https://github.com/Fafa-DL/Opencv-project)
