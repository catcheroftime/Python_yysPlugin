---
title: "阴阳师自动挂机脚本-python"
date: 2019-11-05T19:35:00+08:00
draft: false
Tags:
- python
Categories:
- python
toc: true
img: ""
---

阴阳师每次出现大型活动类似于肝绘卷或者超鬼王之类的，每次的手动简直太伤头发了，太伤肝了，而且每次都是重复性的动作，点击开始，时间一到或者怪一死，进入结算界面之后然后点击结束，一个循环就就结束了，然后重新开始，手动既无聊又累，所有广大玩家想出了很多解放双手的点子，我也不例外，下面简单介绍我是如何用 `python` 实现简单的挂机脚本,先说一下脚本应用的场景，在电脑上运行的阴阳师也就是PC版，在电脑上使用手机模拟器也可以<!--more-->

## 鼠标操作

脚本挂机，最重要的一点类似于人一样对鼠标进行移动和点击，`python` 中 `win32api` 库可以完美实现，下面简单介绍一下脚本中使用到 `win32api` 的地方

> 下载 pip install  pywin32

    # 获取鼠标当前位置的坐标
    def getCurPos():
        return win32gui.GetCursorPos()

    # 鼠标移动到(x,y)位置
    def moveCurPos(x,y):
        win32api.SetCursorPos((x, y))

    # 鼠标点击(x,y)位置
    def mouseLeftClick(x,y):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP,x,y)

其实最后一个函数鼠标点击指定位置，基本已经可以完成脚本关于鼠标控制的功能了

但是阴阳师的地图类似于一个展开的画轴，有的时候需要按住鼠标拖动，所有脚本中我也提供了以下的接口

    class direction():
        UP = 1
        DOWN = 2
        RIGHT = 3
        LEFT = 4

    # 鼠标在(x,y)位置按住, 向指定方向拖动length距离
    def mouseClickedMove(x,y,length,direct):
        moveCurPos(x,y)
        # 鼠标先左击按住
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)    

        x_move = 0
        y_move = 1
        if direct==direction.UP:
            y_move = -1
        elif direct==deirection.DOWN:
            y_move = 1
        elif direct==direction.RIGHT:
            x_move = 1
        elif direct==direction.LEFT:
            x_move = -1
        else:
            print("move direction is error!")

        # 一点点移动的效果
        i = 0
        while i < length:
            time.sleep(0.005)
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,x_move,y_move)
            i = i + 1

        time.sleep(0.2)
        # 鼠标左击最后松开
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

所有可能用到的鼠标操作都封成函数了，之后就是考虑如何点击

## 图片匹配

阴阳师的整体操作无非于鼠标点点点，现在最重要的就是告诉脚本怎么点，我们自己也是通过看到一些特定的图标，然后点击，所有脚本的逻辑也可以这样实现。

### 截图

为了能够识别，首先需要做的事是，截取软件运行时候图片，所以截图是第一步  
这里截图使用的也是 `pywin32` 中的接口

    def window_capture():
        # 获取桌面句柄和桌面的宽度和高度
        desktop_h = win32gui.GetDesktopWindow()
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        # 创建设备描述表
        desktop_dc = win32gui.GetWindowDC(desktop_h)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)
        # 创建一个内存设备描述表
        save_dc  = img_dc.CreateCompatibleDC()
        # 创建位图对象
        capture = win32ui.CreateBitmap()
        capture.CreateCompatibleBitmap(img_dc, width, height)
        save_dc.SelectObject(capture)
        # 保存图片
        save_dc.BitBlt((0, 0), (width, height), img_dc, (0, 0), win32con.SRCCOPY)
        capture.SaveBitmapFile(save_dc , './shotscreen/shot.png')
        # 释放内存
        save_dc.DeleteDC()
        win32gui.DeleteObject(capture.GetHandle())
        win32gui.ReleaseDC(desktop_h,desktop_dc)

其实还有一个特别简单的库 Pillow

> 下载 pip install Pillow

    from PIL import ImageGrab
    
    # 参数说明
    # 第一个参数 开始截图的x坐标
    # 第二个参数 开始截图的y坐标
    # 第三个参数 结束截图的x坐标
    # 第四个参数 结束截图的y坐标
    bbox = (0, 0, 1920, 1080)
    im = ImageGrab.grab(bbox)
    
    # 参数 保存截图文件的路径
    im.save('./shotscreen/shot.png')

直接使用 `Pillow` 截图效率相对于使用 `pywin32` 可能稍微低一点

### 匹配

截图也完成了，那么只剩下图像的匹配了，图像匹配主要使用的是 `opencv` 相关的库对图片进行比较，然后对 `opencv` 处理的结果使用 `numpy` 进行计算，计算出需要点击的位置

> 下载 pip install opencv-python  
> 以及 pip install numpy

    # template 需要被识别出的模板
    # img      桌面截图
    def picMatch(template, img):
        h,w=template.shape[:2]
        res = cv2.cv2.matchTemplate(img,template,cv2.cv2.TM_CCOEFF_NORMED)
        threshold = 0.99             
        gps = []                          
        loc = numpy.where(res >= threshold) 
        for pt in zip(*loc[::-1]):
            pt = (pt[0]+w/2, pt[1]+h/2)
            gps.append(pt)

        return gps

匹配成功会返回若干个满足条件的 [x,y] 的信息，被选出需要识别的图片和桌面截图之间一般只有1个满足条件的坐标，拿到坐标之后，使用鼠标的点击即可

## 整体逻辑

其实对于一个完整的流程

| 阶段                | 脚本行为                 | 备注                                           |
| :------------------ | :----------------------- | :--------------------------------------------- |
| 开始挑战            | 截图，然后识别开始，点击 | 开始界面有动画，多次点击，可以跳过动画         |
| 准备                | 截图，然后识别准备，点击 | 锁住挑战式神阵容，可省略                       |
| 战斗中              | 等待                     | 不同玩法，战斗时间不同                         |
| 战斗(成功/失败)结算 | 截图，然后识别结束，点击 | 结算界面存在动画，脚本多点击几次，可以跳过动画 |
| 重新开始挑战        | 循环                     |                                                |

实际在开发脚本过程中，我的做法是，截一张图，与开始阶段，战斗成功，战斗失败，战斗结算图片匹配，都匹配不到，算是战斗中等待；而展示完整的流程，仅仅只是为了展示一下可能的完美流程，如果战斗中频繁截图，可能会吃电脑资源

    if __name__=='__main__':
        count = 0
        success_time = 0
        failure_time = 0
        while True:
            window_capture()
            img = cv2.cv2.imread('./shotscreen/shot.png')

            start_template = cv2.cv2.imread('./yys/start.png')
            start_position = picMatch(start_template, img)
            if start_position:
                count += 1
                mouseLeftClick(int(start_position[0][0]), int(start_position[0][1]) )
                print("第{}次开始".format(count))
                time.sleep(1)
                mouseLeftClick(int(start_position[0][0]), int(start_position[0][1]) )
                mouseLeftClick(int(start_position[0][0]), int(start_position[0][1]) )
                time.sleep(15)

            failure_template = cv2.cv2.imread('./yys/failure.png')
            failure_position = picMatch(failure_template, img)
            if failure_position:
                failure_time += 1
                mouseLeftClick(int(failure_position[0][0]), int(failure_position[0][1]) )
                print("第{}次挑战失败".format(failure_time))
                mouseLeftClick(int(failure_position[0][0]), int(failure_position[0][1]) )
                mouseLeftClick(int(failure_position[0][0]), int(failure_position[0][1]) )
                time.sleep(3)
            
            success_template = cv2.cv2.imread('./yys/success.png')
            success_position = picMatch(success_template, img)
            if success_position:
                success_time += 1
                mouseLeftClick(int(success_position[0][0]), int(success_position[0][1]) )
                print("第{}次挑战成功".format(success_time))
                mouseLeftClick(int(success_position[0][0]), int(success_position[0][1]) )
                mouseLeftClick(int(success_position[0][0]), int(success_position[0][1]) )
                time.sleep(3)

            settlement_template = cv2.cv2.imread('./yys/settlement.png')
            settlement_position = picMatch(settlement_template, img)
            if settlement_position:
                mouseLeftClick(int(settlement_position[0][0]), int(settlement_position[0][1]) )