
<!-- TOC Marked -->

+ [基于三维人脸数据的AR互动平台开发](#基于三维人脸数据的ar互动平台开发)
    * [我使用的系统 `Manjaro`](#我使用的系统-`manjaro`)
        - [Requirements](#requirements)
        - [运行示例](#运行示例)
    * [人脸表情实时识别](#人脸表情实时识别)
        - [Demo](#demo)
    * [3D模型加载](#3d模型加载)
        - [Demo](#demo)
    * [移植到树莓派上](#移植到树莓派上)
        - [基础配置](#基础配置)
        - [实现环境配置](#实现环境配置)
    * [可能遇到的问题：](#可能遇到的问题：)
+ [参考与感谢](#参考与感谢)

<!-- /TOC -->
# 基于三维人脸数据的AR互动平台开发

根据已有的三维人脸数据，开发一款基于普通投影仪或显示器和普通相机的人机交互系统，要求
1. 实现三维人脸的渲染和显示；
2. 能识别相机前实时采集的面部表情，比如大笑、沮丧等；能根据面部表情变化对应调整三维人脸数据；
3. 其他个性发挥延拓功能。

## 我使用的系统 `Manjaro`

![manjaro](/readme_use/system_show.png)

### Requirements

```sh
pip install pygame
pip install deepface
pip install tensorflow
pip install PyOpenGL PyOpenGL_accelerate
pip install numpy
pip install opencv-python
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

使用`pyopengl`进行3d模型的加载

### Demo

1. obj_show.py

![](/readme_use/obj_show_test.png)

You can use mouse to move, rotate and scale it. And you may set lighting for a better viewing. You need to be familiar with opengl.

(鼠标移动，自行设置光照，具体可以看代码)

See the code to learn more. (eg. I use `pickle` to accelerate loading)

## 移植到树莓派上

其实并不推荐使用树莓派，它的处理速度着实慢。很多地方都会卡。

我使用的是树莓派官方的系统(这里跳过安装)。

### 基础配置

1. 更换软件源（这里使用的是清华的源）

    1. `sudo nano /etc/apt/sources.list`注释掉原来的源，加上
    ```sh
    deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ buster main non-free contrib rpi
    deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ buster main non-free contrib rpi
    ```

    2. `sudo nano /etc/apt/sources.list.d/raspi.list`同样注释掉原来的源，加上
    ```sh
    deb http://mirrors.tuna.tsinghua.edu.cn/raspberrypi/ buster main
    deb-src http://mirrors.tuna.tsinghua.edu.cn/raspberrypi/ buster main
    ```

    3. 更新软件源`sudo apt-get uopdate`.

    推荐软件
        - ranger:终端文件管理器
        - vim 或 neovim:编辑器
        - python3, python3-dev:编程环境

2. 无线网络配置

    1. 有屏幕的话直接连接，不用多说

    2. 没有屏幕如何链接
    > 如果遇到中文wifi可能也无法直接连接。
    > 可以通过修改配置文件的方式来实现
    >
    > sudo vim /etc/wpa_supplicant/wpa_supplicant.conf
    > ```sh
    > network={
    >    ssid="ssid_name"
    >    key_mgmt=WPA-PSK
    >    psk="password"
    > }
    > ```

3. 添加3.5寸显示屏驱动

```sh
sudo rm -rf LCD-show
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show/
sudo ./LCD35-show
```

4. 其他配置，如打开vnc和摄像头，可以通过`sudo raspi-config`来实现。
更多配置请参考 [树莓派实验室](https://shumeipai.nxez.com/hot-explorer#beginner)

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

