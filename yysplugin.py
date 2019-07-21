import cv2
import numpy
from PIL import ImageGrab
from PIL import Image,ImageChops
import time
import win32gui
import win32con
import win32api

# 鼠标移动到(x,y)位置
def moveCurPos(x,y):
    win32api.SetCursorPos((x, y))

# 鼠标点击(x,y)位置
def mouseLeftClick(x,y):
    moveCurPos(x,y)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)


# 鼠标在(x,y)位置按住, 向左拖动length距离
def mouseClickedLeftMove(x,y,length):
    moveCurPos(x,y)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0,0,0)    
    i = 0
    while i < length:
        time.sleep(0.005)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE,-1,0,0,0)
        i = i + 1

    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

# 获取鼠标当前位置的坐标
def getCurPos():
    return win32gui.GetCursorPos()

def location(template, img):
    h,w=template.shape[:2]
    res = cv2.cv2.matchTemplate(img,template,cv2.cv2.TM_CCOEFF_NORMED)
    threshold = 0.99             
    gps = []                          
    loc = numpy.where(res >= threshold) 
    for pt in zip(*loc[::-1]):
        pt = (pt[0]+w/2, pt[1]+h/2)
        gps.append(pt)

    return gps


if __name__=='__main__':
    time.sleep(2)
    while True:
        # ret = getCurPos()
        # mouseClickedLeftMove(ret[0],ret[1],300)

        bbox = (0, 0, 1920, 1080)
        shotscreen = ImageGrab.grab(bbox)    
        shotscreen.save('./shotscreen/shot.png')
        img = cv2.cv2.imread('./shotscreen/shot.png')

        failure_template = cv2.cv2.imread('./yys/failure.png')
        failure_position = location(failure_template, img)
        if failure_position:
            mouseLeftClick(int(failure_position[0][0]), int(failure_position[0][1]) )
            print("挑战失败,重新开始")

        success_template = cv2.cv2.imread('./yys/end.png')
        success_position = location(success_template, img)
        if success_position:
            mouseLeftClick(int(success_position[0][0]), int(success_position[0][1]) )
            print("挑战成功, 再次开始")
            time.sleep(2)
            mouseLeftClick(int(success_position[0][0]), int(success_position[0][1]) )
            mouseLeftClick(int(success_position[0][0]), int(success_position[0][1]) )

        start_template = cv2.cv2.imread('./yys/start.png')
        start_position = location(start_template, img)
        if start_position:
            mouseLeftClick(int(start_position[0][0]), int(start_position[0][1]) )
            print("开始")
            time.sleep(15)

