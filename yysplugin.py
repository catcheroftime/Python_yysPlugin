import cv2
import numpy
import time
import win32gui
import win32con
import win32api
import win32ui


# 获取鼠标当前位置的坐标
def getCurPos():
    return win32gui.GetCursorPos()

# 鼠标移动到(x,y)位置
def moveCurPos(x,y):
    win32api.SetCursorPos((x, y))

# 鼠标点击(x,y)位置
def mouseLeftClick(x,y):
    moveCurPos(x,y)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

class direction():
    UP = 1
    DOWN = 2
    RIGHT = 3
    LEFT = 4

# 鼠标在(x,y)位置按住, 向指定方向拖动length距离
def mouseClickedMove(x,y,length,direct):
    moveCurPos(x,y)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)    

    x_move = 0
    y_move = 1
    if direct==direction.UP:
        y_move = -1
    elif direct==direction.DOWN:
        y_move = 1
    elif direct==direction.RIGHT:
        x_move = 1
    elif direct==direction.LEFT:
        x_move = -1 
    else:
        print("move direction is error!")

    i = 0
    while i < length:
        time.sleep(0.005)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,x_move,y_move)
        i = i + 1

    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

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
    capture.SaveBitmapFile(save_dc , './yys/shot.png')
    # 释放内存
    save_dc.DeleteDC()
    win32gui.DeleteObject(capture.GetHandle())
    win32gui.ReleaseDC(desktop_h,desktop_dc)

def clickPosition(positions, time=3):
    for pos in positions:
        i = 0
        while i<time:
            mouseLeftClick(int(pos[0]), int(pos[1]) )
            i += 1


if __name__=='__main__':
    count = 0
    success_time = 0
    failure_time = 0
    while True:
        window_capture()
        img = cv2.cv2.imread('./yys/shot.png')

        ready_template = cv2.cv2.imread('./yys/ready.png')
        ready_position = picMatch(ready_template, img)
        if ready_position:
            clickPosition(ready_position,1)
            time.sleep(15)
            continue

        failure_template = cv2.cv2.imread('./yys/failure.png')
        failure_position = picMatch(failure_template, img)
        if failure_position:
            failure_time += 1
            clickPosition(failure_position)
            print("第{}次挑战失败".format(failure_time))
            time.sleep(1)
            continue
        
        success_template = cv2.cv2.imread('./yys/success.png')
        success_position = picMatch(success_template, img)
        if success_position:
            success_time += 1
            clickPosition(success_position)
            print("第{}次挑战成功".format(success_time))
            time.sleep(1)
            continue

        start_template = cv2.cv2.imread('./yys/start.png')
        start_position = picMatch(start_template, img)
        if start_position:
            count += 1
            clickPosition(start_position)
            print("第{}次开始".format(count))
            time.sleep(3)
            continue

        settlement_template = cv2.cv2.imread('./yys/settlement.png')
        settlement_position = picMatch(settlement_template, img)
        if settlement_position:
            clickPosition(settlement_position)
            time.sleep(1)
            continue



