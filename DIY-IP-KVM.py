# -*- coding: utf-8 -*-

import os
import cv2
import sys
import time
import serial  # pip install pyserial
import numpy as np
import logging
import datetime
import platform
import pyautogui
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from threading import Thread
from configparser import ConfigParser
if platform.system().lower() == 'windows':
    import win32api
    import win32con


import KeyboardCommandDefinition


g_strProgramName = 'DIY-IP-KVM'
g_iWidth, g_iHeight = 1024, 768  # 屏幕宽度 屏幕高度
g_iVideoDeviceIndex = 0  # USB采集卡索引
g_iVideoDeviceFPS = 60  # FPS帧率
g_iVideoDeviceImageOutputFormat = 1  # 图像输出格式 1：YUY2 2：MJPG
g_strSerialDeviceName = ''  # USBHID设备名称 Linux:/dev/ttyUSB0 | Windows:COM3
g_iHideLocalMouse = 0
g_iMouseOffsetX, g_iMouseOffsetY = 0, 0
g_iMousePositionMethod = 2  # 鼠标定位方法 1：绝对定位 2：相对定位（推荐）


DEFVAR_MAXMOUSEMOVEVALUE = 127  # 鼠标单次最大可移动的数值（设备要求范围1-127）

g_serial_com = None
g_Exit = False
g_Exit_Thread_Mouse = False
g_GrabScreen = False
g_MouseHasBeenCaptured = False  # 是否捕获住鼠标，只有相对定位才使用。

g_ResolutionTable = [
    [1920, 1080],
    [1600, 1200],
    [1360, 768],
    [1280, 1024],
    [1280, 960],
    [1280, 720],
    [1024, 768],
    [800, 600],
    [720, 576],
    [720, 480],
    [640, 480]
]


def Fun_WriteLog(strLog):
    try:
        logging.basicConfig(filename='%s.log' % g_strProgramName,
                            level=logging.INFO)  # encoding='utf-8',
        strDateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(strDateTime + ': ' + str(strLog))
    except Exception:
        pass


def Fun_CloseWindow():
    global g_Exit_Thread_Mouse, g_Exit

    g_Exit_Thread_Mouse = True
    g_Exit = True


def Fun_VideoInit():
    if platform.system().lower() == 'windows':
        cap = cv2.VideoCapture(g_iVideoDeviceIndex, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(g_iVideoDeviceIndex)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, g_iWidth)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, g_iHeight)
    cap.set(cv2.CAP_PROP_FPS, g_iVideoDeviceFPS)  # FPS帧率
    if g_iVideoDeviceImageOutputFormat == 1:
        # YUY2 CV_CAP_PROP_FOURCC:6
        cap.set(6, int.from_bytes(b'YUY2', "little"))
    elif g_iVideoDeviceImageOutputFormat == 2:
        # MJPG CV_CAP_PROP_FOURCC:6
        cap.set(6, int.from_bytes(b'MJPG', "little"))
    else:
        # YUY2 CV_CAP_PROP_FOURCC:6
        cap.set(6, int.from_bytes(b'YUY2', "little"))

    return cap


def Fun_ShowVideo():
    global g_GrabScreen

    cap = Fun_VideoInit()
    if cap.isOpened():
        iWidth, iHeight = g_iWidth, g_iHeight
        while (g_Exit is False):
            if iWidth != g_iWidth and iHeight != g_iHeight:  # 修改分辨率了
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, g_iWidth)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, g_iHeight)
                iWidth, iHeight = g_iWidth, g_iHeight
            bRet, Frame = cap.read()
            if bRet is True:
                # 捕获屏幕
                if g_GrabScreen is True:
                    g_GrabScreen = False
                    try:
                        if not os.path.exists('./Screenshot'):
                            os.mkdir('./Screenshot')
                        cv2.imwrite('./Screenshot/Screenshot_' + time.strftime('%Y-%m-%d %H-%M-%S', time.localtime()) + '.png',
                                    Frame)  # 保存路径
                    except Exception:
                        pass
                # 捕获屏幕
                # 将图像的通道顺序由BGR转换成RGB
                Frame = cv2.cvtColor(Frame, cv2.COLOR_BGR2RGB)
                if isinstance(Frame, np.ndarray):
                    Frame = Image.fromarray(Frame.astype(np.uint8))

                photo = ImageTk.PhotoImage(image=Frame)
                VideoControl.create_image([cap.get(cv2.CAP_PROP_FRAME_WIDTH) / 2,
                                           cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2], image=photo)

                Window.update_idletasks()
                Window.update()
    else:
        messagebox.showerror(title=g_strProgramName +
                             ' 软件', message='打开采集卡设备失败，请检查配置文件是否配置正确。')
    cap.release()
    cv2.destroyAllWindows()
    if g_serial_com.is_open:
        g_serial_com.close()  # 关闭串口
    Fun_SaveConfigFile()
    Window.quit()


def Fun_GetHIDDeviceCode(iKeyCode, iState):
    iLocation = 0
    if iState & 0x40000 == 0x40000:
        iLocation = 1
    for KeyValue in KeyboardCommandDefinition.g_KeyValueTable:
        if platform.system().lower() == 'windows':
            if KeyValue[0] == iKeyCode and KeyValue[1] == iLocation:
                return KeyValue[3]
        else:
            if KeyValue[2] == iKeyCode:
                return KeyValue[3]
    return None


def Fun_SetBitVal(byte, index, val):
    """
    更改某个字节中某一位（Bit）的值

    :param byte: 准备更改的字节原值
    :param index: 待更改位的序号，从右向左0开始，0-7为一个完整字节的8个位
    :param val: 目标位预更改的值，0或1
    :returns: 返回更改后字节的值
    """
    if val:
        return byte | (1 << index)
    else:
        return byte & ~(1 << index)


def Fun_WriteSerial(strCommand):
    if len(strCommand):
        try:
            # print(strCommand)
            if g_serial_com.is_open:
                g_serial_com.write(strCommand.encode('utf-8'))  # 发送串口指令
                ''' # 下列代码可以读取串口返回内容
                bufferBytes = g_serial_com.inWaiting()
                RadBytes = g_serial_com.read(bufferBytes)
                print(RadBytes)
                '''
        except Exception:
            pass


def Fun_Callback_Keyboard(event):
    global g_Exit_Thread_Mouse, g_MouseHasBeenCaptured
    # print(event, '\nkeycode(hex):%02X, state(hex):%X' % (event.keycode, event.state))
    # return None
    # 释放鼠标
    if g_iMousePositionMethod == 2 and g_MouseHasBeenCaptured is True:
        if event.keycode == 0xE5:
            g_Exit_Thread_Mouse = True
            g_MouseHasBeenCaptured = False
            Fun_SetStatusBar()
            VideoControl.config(cursor='')
    # 释放鼠标
    Ctrl = (event.state & 0x4) != 0
    Alt = (event.state & 0x20000) != 0
    Shift = (event.state & 0x1) != 0
    Win = event.keycode == 0x5B

    Byte_FunctionKeyMark = 0x00
    # bit0: Left Control 是否按下，按下为 1
    Byte_FunctionKeyMark = Fun_SetBitVal(Byte_FunctionKeyMark, 0, Ctrl)
    # bit1: Left Shift 是否按下，按下为 1
    Byte_FunctionKeyMark = Fun_SetBitVal(Byte_FunctionKeyMark, 1, Shift)
    # bit2: Left Alt 是否按下，按下为 1
    Byte_FunctionKeyMark = Fun_SetBitVal(Byte_FunctionKeyMark, 2, Alt)
    # bit3: Left GUI 是否按下，按下为 1
    Byte_FunctionKeyMark = Fun_SetBitVal(Byte_FunctionKeyMark, 3, Win)
    # bit4: Right Control 是否按下，按下为 1
    Byte_FunctionKeyMark = Fun_SetBitVal(Byte_FunctionKeyMark, 4, 0)
    # bit5: Right Shift 是否按下，按下为 1
    Byte_FunctionKeyMark = Fun_SetBitVal(Byte_FunctionKeyMark, 5, 0)
    # bit6: Right Alt 是否按下，按下为 1
    Byte_FunctionKeyMark = Fun_SetBitVal(Byte_FunctionKeyMark, 6, 0)
    # bit7: Right GUI 是否按下，按下为 1
    Byte_FunctionKeyMark = Fun_SetBitVal(Byte_FunctionKeyMark, 7, 0)

    # print('\nByte_FunctionKeyMark: %02X' % Byte_FunctionKeyMark)

    # print(event, '\nCtrl:%d Alt:%d Shift:%d' % (Ctrl, Alt, Shift))
    iHIDDeviceCode = Fun_GetHIDDeviceCode(event.keycode, event.state)
    if iHIDDeviceCode is not None:
        # cmd = '[kD%02X][kU%02X]' % (iHIDDeviceCode, iHIDDeviceCode)
        cmd = '[K%02X00%02X0000000000][K0000000000000000]' % (
            Byte_FunctionKeyMark, iHIDDeviceCode)
        # print(cmd)
        Fun_WriteSerial(cmd)


def Fun_Callback_Mouse_Enter(event):
    if event.state & 0x0100 or event.state & 0x0200 or event.state & 0x0400:
        return  # Linux下鼠标点击也会触发，所以对点击事件做出过滤。
    global g_Exit_Thread_Mouse
    g_Exit_Thread_Mouse = False
    if g_iMousePositionMethod == 1:
        if g_iHideLocalMouse:
            VideoControl.config(cursor="none")
        Fun_TakeOverMouse(Window, VideoControl)


def Fun_Callback_Mouse_Leave(event):
    if event.state & 0x0100 or event.state & 0x0200 or event.state & 0x0400:
        return  # Linux下鼠标点击也会触发，所以对点击事件做出过滤。
    global g_Exit_Thread_Mouse
    if g_iMousePositionMethod == 1:
        g_Exit_Thread_Mouse = True


def Fun_Callback_Mouse_Button(event):
    global g_MouseHasBeenCaptured
    if g_iMousePositionMethod == 2 and g_MouseHasBeenCaptured is False:
        g_MouseHasBeenCaptured = True
        if g_iHideLocalMouse or g_iMousePositionMethod == 2:
            VideoControl.config(cursor="none")
        Fun_SetStatusBar()
        Fun_TakeOverMouse(Window, VideoControl)
    # print(event)
    if g_Exit_Thread_Mouse is False:
        if event.num == 1:
            Fun_WriteSerial('[MDL]')
        elif event.num == 2:
            Fun_WriteSerial('[MDM]')
        elif event.num == 3:
            Fun_WriteSerial('[MDR]')


def Fun_Callback_Mouse_ButtonRelease(event):
    # print(event)
    if g_Exit_Thread_Mouse is False:
        if event.num == 1:
            Fun_WriteSerial('[MUL]')
        elif event.num == 2:
            Fun_WriteSerial('[MUM]')
        elif event.num == 3:
            Fun_WriteSerial('[MUR]')


def Fun_Callback_Mouse_Wheel(event):
    # print(event)
    if event.delta > 0:
        Fun_WriteSerial('[MGU1]')  # 鼠标滚轮向上 [MGU1]，红色部分为可选值，有效范围 1~4
    elif event.delta < 0:
        Fun_WriteSerial('[MGD1]')  # 鼠标滚轮向下 [MGD1] ，红色部分为可选值，有效范围 1~4


def Fun_MoveControlledMouse_Base_Oblique(strCommand, X_RP_ABS, Y_RP_ABS):
    iMouseMoveCount = max(X_RP_ABS, Y_RP_ABS) // DEFVAR_MAXMOUSEMOVEVALUE
    if max(X_RP_ABS, Y_RP_ABS) % DEFVAR_MAXMOUSEMOVEVALUE:
        iMouseMoveCount += 1

    iX_MaxRangeOfSingleMove, iY_MaxRangeOfSingleMove = X_RP_ABS // iMouseMoveCount, Y_RP_ABS // iMouseMoveCount
    if X_RP_ABS % iMouseMoveCount:
        iX_MaxRangeOfSingleMove += 1
    if Y_RP_ABS % iMouseMoveCount:
        iY_MaxRangeOfSingleMove += 1

    strCMD = ''
    iX, iY = X_RP_ABS, Y_RP_ABS
    i = 0
    while i < iMouseMoveCount:
        if i + 1 != iMouseMoveCount:
            iX -= iX_MaxRangeOfSingleMove
            iY -= iY_MaxRangeOfSingleMove
            strCMD = '[%s%d,%d]' % (strCommand,
                                    iX_MaxRangeOfSingleMove,
                                    iY_MaxRangeOfSingleMove)
        else:
            strCMD = '[%s%d,%d]' % (strCommand, iX, iY)
        Fun_WriteSerial(strCMD)
        i += 1


def Fun_MoveControlledMouse_Base_Straight(strCommand, RP_ABS):
    iMouseMoveCount = RP_ABS // DEFVAR_MAXMOUSEMOVEVALUE
    if RP_ABS % DEFVAR_MAXMOUSEMOVEVALUE:
        iMouseMoveCount += 1

    iMaxRangeOfSingleMove = RP_ABS // iMouseMoveCount
    if RP_ABS % iMouseMoveCount:
        iMaxRangeOfSingleMove += 1

    strCMD = ''
    iRP = RP_ABS
    i = 0
    while i < iMouseMoveCount:
        if i + 1 != iMouseMoveCount:
            iRP -= iMaxRangeOfSingleMove
            strCMD = '[%s%d]' % (strCommand, iMaxRangeOfSingleMove)
        else:
            strCMD = '[%s%d]' % (strCommand, iRP)
        Fun_WriteSerial(strCMD)
        i += 1


def Fun_MoveControlledMouse(X_RP, Y_RP, X_RP_ABS, Y_RP_ABS):
    if X_RP_ABS and Y_RP_ABS:  # 斜向位
        if X_RP > 0 and Y_RP > 0:
            Fun_MoveControlledMouse_Base_Oblique('MM7', X_RP_ABS, Y_RP_ABS)
        elif X_RP < 0 and Y_RP < 0:
            Fun_MoveControlledMouse_Base_Oblique('MM6', X_RP_ABS, Y_RP_ABS)
        elif X_RP > 0 and Y_RP < 0:
            Fun_MoveControlledMouse_Base_Oblique('MM8', X_RP_ABS, Y_RP_ABS)
        elif X_RP < 0 and Y_RP > 0:
            Fun_MoveControlledMouse_Base_Oblique('MM5', X_RP_ABS, Y_RP_ABS)
        # print("斜向位")
    else:  # 垂向位
        if X_RP_ABS:
            if X_RP > 0:
                Fun_MoveControlledMouse_Base_Straight('MM4', X_RP_ABS)
            else:
                Fun_MoveControlledMouse_Base_Straight('MM3', X_RP_ABS)
        else:
            if Y_RP > 0:
                Fun_MoveControlledMouse_Base_Straight('MM1', Y_RP_ABS)
            else:
                Fun_MoveControlledMouse_Base_Straight('MM2', Y_RP_ABS)
        # print("垂向位")


def Fun_SetScreenResolution(iWidth, iHeight):
    global g_iWidth, g_iHeight
    g_iWidth, g_iHeight = iWidth, iHeight
    VideoControl.config(width=iWidth, height=iHeight)
    Window.eval('tk::PlaceWindow . center')


def Fun_TakeOverMouse_Thread(Window, VideoControl):
    if g_iMousePositionMethod == 1:
        Fun_TakeOverMouse_AnalogAbsolute(Window, VideoControl)
    elif g_iMousePositionMethod == 2:
        Fun_TakeOverMouse_Relatively(Window, VideoControl)


def Fun_TakeOverMouse_Relatively(Window, VideoControl):
    iScreenWidth, iScreenHeight = pyautogui.size()  # 获取屏幕宽高

    iWindowCaptionHeight = 0
    iCXFrame = iCYFrame = 0
    iCXBorder = iCYBorder = 0
    iCXPaddedBorder = 0
    iMainMenuHeight = 0
    if platform.system().lower() == 'windows':
        iWindowCaptionHeight = win32api.GetSystemMetrics(win32con.SM_CYCAPTION)
        iCXFrame = win32api.GetSystemMetrics(win32con.SM_CXFRAME)
        iCYFrame = win32api.GetSystemMetrics(win32con.SM_CYFRAME)
        iCXBorder = win32api.GetSystemMetrics(win32con.SM_CXBORDER)
        iCYBorder = win32api.GetSystemMetrics(win32con.SM_CYBORDER)
        iCXPaddedBorder = win32api.GetSystemMetrics(92)
        iMainMenuHeight = 20  # 通过代码不知道为什么无法获取，代码获取总返回1，网上也有人反应。
    # print(iWindowCaptionHeight, iCXFrame, iCYFrame,
    #      iCXBorder, iCYBorder, iCXPaddedBorder)
    iWindow_X, iWindow_Y = Window.winfo_x(), Window.winfo_y()
    iVideoControl_X, iVideoControl_Y = VideoControl.winfo_x(), VideoControl.winfo_y()
    iVideoControl_Width, iVideoControl_Height = \
        VideoControl.winfo_width(), \
        VideoControl.winfo_height()
    iMouse_X_Base, iMouse_Y_Base = pyautogui.position()  # 返回鼠标的坐标

    # 计算鼠标限制在对话框中的范围值
    iWidth_Ratio, iHeight_Ratio = int((iVideoControl_Width - iVideoControl_Width * 0.80) / 2), \
        int((iVideoControl_Height - iVideoControl_Height * 0.80) / 2)
    # 计算鼠标限制在对话框中的范围值

    # j计算鼠标指针默认回归点位
    iRegressionPointX = iWindow_X + iVideoControl_X + iCXFrame - \
        iCXBorder + iCXPaddedBorder + iVideoControl_Width / 2
    iRegressionPointY = iWindow_Y + iVideoControl_Y + iCYFrame + iCYBorder + \
        iCXPaddedBorder + iWindowCaptionHeight + \
        iMainMenuHeight + iVideoControl_Height / 2
    # j计算鼠标指针默认回归点位

    while (g_Exit_Thread_Mouse is False):
        iMouse_X_Cur, iMouse_Y_Cur = pyautogui.position()  # 返回鼠标的坐标
        if iMouse_X_Base != iMouse_X_Cur or iMouse_Y_Base != iMouse_Y_Cur:
            # 限制鼠标活动范围
            iMouse_X_Cur_RelativeVideoControl = iMouse_X_Cur - \
                iWindow_X - iVideoControl_X - iCXFrame - iCXBorder - \
                iCXPaddedBorder  # 当前鼠标相对VideoControl控件的X坐标
            iMouse_Y_Cur_RelativeVideoControl = iMouse_Y_Cur - iWindow_Y - \
                iVideoControl_Y - iCYFrame - iCYBorder - iCXPaddedBorder - iWindowCaptionHeight - \
                iMainMenuHeight  # 当前鼠标相对VideoControl控件的Y坐标

            if iMouse_X_Cur_RelativeVideoControl < iWidth_Ratio or iMouse_X_Cur_RelativeVideoControl > iVideoControl_Width - iWidth_Ratio \
                    or iMouse_Y_Cur_RelativeVideoControl < iHeight_Ratio or iMouse_Y_Cur_RelativeVideoControl > iVideoControl_Height - iHeight_Ratio:
                pyautogui.moveTo(iRegressionPointX, iRegressionPointY)
                iMouse_X_Base, iMouse_Y_Base = pyautogui.position()  # 返回鼠标的坐标
                continue
            # print(iMouse_X_Cur_RelativeVideoControl, iMouse_Y_Cur_RelativeVideoControl)
            # 限制鼠标活动范围
            # print("[Mouse_X_Base:%d Mouse_Y_Base:%d] - [Mouse_X_Cur:%d Mouse_Y_Cur:%d] - [Window_X:%d Window_Y:%d] - [VideoControl_X:%d VideoControl_Y:%d VideoControl_W:%d VideoControl_H:%d] - [WindowCaptionHeight:%d]\n" %
            #      (iMouse_X_Base, iMouse_Y_Base, iMouse_X_Cur, iMouse_Y_Cur, iWindow_X, iWindow_Y, iVideoControl_X, iVideoControl_Y, iVideoControl_Width, iVideoControl_Height, iWindowCaptionHeight))
            X_RP, Y_RP = iMouse_X_Cur - iMouse_X_Base, \
                iMouse_Y_Base - iMouse_Y_Cur  # 坐标差值
            X_RP_ABS, Y_RP_ABS = abs(X_RP), abs(Y_RP)  # 坐标差值abs
            # print(X_RP_ABS, Y_RP_ABS)

            Fun_MoveControlledMouse(X_RP, Y_RP, X_RP_ABS, Y_RP_ABS)
            iMouse_X_Base, iMouse_Y_Base = iMouse_X_Cur, iMouse_Y_Cur


def Fun_TakeOverMouse_AnalogAbsolute(Window, VideoControl):
    Fun_MoveControlledMouse(-1, 1, g_iWidth, g_iHeight)  # 将受控端鼠标坐标设置成0,0点。

    iWindowCaptionHeight = 0
    iCXFrame = iCYFrame = 0
    iCXBorder = iCYBorder = 0
    iCXPaddedBorder = 0
    iMainMenuHeight = 0
    if platform.system().lower() == 'windows':
        iWindowCaptionHeight = win32api.GetSystemMetrics(win32con.SM_CYCAPTION)
        iCXFrame = win32api.GetSystemMetrics(win32con.SM_CXFRAME)
        iCYFrame = win32api.GetSystemMetrics(win32con.SM_CYFRAME)
        iCXBorder = win32api.GetSystemMetrics(win32con.SM_CXBORDER)
        iCYBorder = win32api.GetSystemMetrics(win32con.SM_CYBORDER)
        iCXPaddedBorder = win32api.GetSystemMetrics(92)
        iMainMenuHeight = 20  # 通过代码不知道为什么无法获取，代码获取总返回1，网上也有人反应。
    # print(iWindowCaptionHeight, iCXFrame, iCYFrame,
    #      iCXBorder, iCYBorder, iCXPaddedBorder)
    iWindow_X, iWindow_Y = Window.winfo_x(), Window.winfo_y()
    iVideoControl_X, iVideoControl_Y = VideoControl.winfo_x(), VideoControl.winfo_y()
    iMouse_X_Base, iMouse_Y_Base = pyautogui.position()  # 返回鼠标的坐标

    # 后将受控端鼠标坐标设置成当前坐标点。
    iMouse_X_Cur_RelativeVideoControl = iMouse_X_Base - \
        iWindow_X - iVideoControl_X  # 当前鼠标相对VideoControl控件的X坐标
    iMouse_Y_Cur_RelativeVideoControl = iMouse_Y_Base - iWindow_Y - \
        iVideoControl_Y - iWindowCaptionHeight - \
        iMainMenuHeight  # 当前鼠标相对VideoControl控件的Y坐标
    # print(iMouse_X_Cur_RelativeVideoControl,
    #      iMouse_Y_Cur_RelativeVideoControl)

    Fun_MoveControlledMouse(1,
                            -1,
                            iMouse_X_Cur_RelativeVideoControl - iCXFrame -
                            iCXPaddedBorder - iCXBorder + g_iMouseOffsetX,
                            iMouse_Y_Cur_RelativeVideoControl - iCYFrame -
                            iCXPaddedBorder - iCYBorder + g_iMouseOffsetY)
    # 后将受控端鼠标坐标设置成当前坐标点。

    while (g_Exit_Thread_Mouse is False):
        iMouse_X_Cur, iMouse_Y_Cur = pyautogui.position()  # 返回鼠标的坐标
        if iMouse_X_Base != iMouse_X_Cur or iMouse_Y_Base != iMouse_Y_Cur:
            # print("[Mouse_X_Base:%d Mouse_Y_Base:%d] - [Mouse_X_Cur:%d Mouse_Y_Cur:%d] - [Window_X:%d Window_Y:%d] - [VideoControl_X:%d VideoControl_Y:%d] - [WindowCaptionHeight:%d]\n" %
            #      (iMouse_X_Base, iMouse_Y_Base, iMouse_X_Cur, iMouse_Y_Cur, iWindow_X, iWindow_Y, iVideoControl_X, iVideoControl_Y, iWindowCaptionHeight))
            X_RP, Y_RP = iMouse_X_Cur - iMouse_X_Base, \
                iMouse_Y_Base - iMouse_Y_Cur  # 坐标差值
            X_RP_ABS, Y_RP_ABS = abs(X_RP), abs(Y_RP)  # 坐标差值abs
            # print(X_RP_ABS, Y_RP_ABS)
            Fun_MoveControlledMouse(X_RP, Y_RP, X_RP_ABS, Y_RP_ABS)
            iMouse_X_Base, iMouse_Y_Base = iMouse_X_Cur, iMouse_Y_Cur


def Fun_TakeOverMouse(Window, VideoControl):
    Thread_Mouse = Thread(
        target=Fun_TakeOverMouse_Thread, args=(Window, VideoControl))
    Thread_Mouse.start()


def Fun_LoadConfigFile():
    global g_iVideoDeviceIndex, \
        g_iVideoDeviceFPS, \
        g_iVideoDeviceImageOutputFormat, \
        g_strSerialDeviceName, \
        g_iWidth, g_iHeight, \
        g_iHideLocalMouse, \
        g_iMouseOffsetX, \
        g_iMouseOffsetY, \
        g_iMousePositionMethod

    g_iWidth, g_iHeight = 1024, 768  # 屏幕宽度 屏幕高度
    g_iVideoDeviceIndex = 0  # USB采集卡索引
    g_iVideoDeviceFPS = 60  # FPS帧率
    g_iVideoDeviceImageOutputFormat = 1  # 图像输出格式 1：YUY2 2：MJPG
    g_iMousePositionMethod = 2  # 鼠标定位方法 1：绝对定位 2：相对定位（推荐）

    # USBHID设备名称 Linux:/dev/ttyUSB0 | Windows:COM3
    g_strSerialDeviceName = 'COM3' if platform.system(
    ).lower() == 'windows' else '/dev/ttyUSB0'

    g_iHideLocalMouse = 0
    g_iMouseOffsetX, g_iMouseOffsetY = 0, 0

    config = ConfigParser()
    if config.read('config.ini', encoding='utf-8'):
        try:
            g_iVideoDeviceIndex = (int)(config['Hardware']['VideoDeviceIndex'])
        except Exception:
            pass
        try:
            g_iVideoDeviceFPS = (int)(config['Hardware']['VideoDeviceFPS'])
        except Exception:
            pass
        try:
            g_iVideoDeviceImageOutputFormat = (int)(
                config['Hardware']['VideoDeviceImageOutputFormat'])
        except Exception:
            pass
        try:
            g_strSerialDeviceName = config['Hardware']['HIDSerialDeviceName']
        except Exception:
            pass
        try:
            g_iWidth = (int)(config['Parameter']['DisplayResolution_Width'])
        except Exception:
            pass
        try:
            g_iHeight = (int)(config['Parameter']['DisplayResolution_Height'])
        except Exception:
            pass
        try:
            g_iHideLocalMouse = (int)(config['Parameter']['HideLocalMouse'])
        except Exception:
            pass
        try:
            g_iMouseOffsetX = (int)(config['Parameter']['MouseOffsetX'])
        except Exception:
            pass
        try:
            g_iMouseOffsetY = (int)(config['Parameter']['MouseOffsetY'])
        except Exception:
            pass
        try:
            g_iMousePositionMethod = (int)(
                config['Parameter']['MousePositionMethod'])
        except Exception:
            pass


def Fun_SaveConfigFile():
    config = ConfigParser()
    config['Hardware'] = {}
    config['Hardware']['VideoDeviceIndex'] = str(g_iVideoDeviceIndex)
    config['Hardware']['VideoDeviceFPS'] = str(g_iVideoDeviceFPS)
    config['Hardware']['VideoDeviceImageOutputFormat'] = str(
        g_iVideoDeviceImageOutputFormat)
    config['Hardware']['HIDSerialDeviceName'] = g_strSerialDeviceName
    config['Parameter'] = {}
    config['Parameter']['DisplayResolution_Width'] = str(g_iWidth)
    config['Parameter']['DisplayResolution_Height'] = str(g_iHeight)
    config['Parameter']['HideLocalMouse'] = str(g_iHideLocalMouse)
    config['Parameter']['MouseOffsetX'] = str(g_iMouseOffsetX)
    config['Parameter']['MouseOffsetY'] = str(g_iMouseOffsetY)
    config['Parameter']['MousePositionMethod'] = str(g_iMousePositionMethod)
    with open('config.ini', 'w', encoding='utf-8') as ConfigFile:
        config.write(ConfigFile)


def DialogCenter(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


class DialogSetup(tk.Toplevel, object):
    try:
        def __init__(self, parent):
            tk.Toplevel.__init__(self, parent)

            self.transient(parent)
            self.withdraw()
            if platform.system().lower() == 'windows':
                try:
                    self.iconbitmap('resource/%s.ico' % g_strProgramName)
                except Exception:
                    pass
            self.title('设置')
            self.resizable(False, False)
            self.grab_set()
            self.protocol('WM_DELETE_WINDOW', self.destroy)

            Label_Resolution = tk.Label(self, text="目标设备屏幕分辨率")
            Label_Resolution.pack()
            # 初始化分辨率控件
            iCurrentIndex = -1
            Resolution_Arrays = []  # 构建分辨率数组
            for index, Resolution in enumerate(g_ResolutionTable):
                if g_iWidth == Resolution[0] and g_iHeight == Resolution[1]:
                    iCurrentIndex = index
                Resolution_Arrays.append(
                    '%d x %d' % (Resolution[0], Resolution[1]))
            self.Combobox_Resolution = ttk.Combobox(self)
            self.Combobox_Resolution.configure(state="readonly")
            self.Combobox_Resolution['values'] = Resolution_Arrays
            self.Combobox_Resolution.bind(
                "<<ComboboxSelected>>", self.Fun_Combobox_Resolution_Selected)
            if iCurrentIndex != -1:
                self.Combobox_Resolution.current(iCurrentIndex)
            self.Combobox_Resolution.pack()
            # 初始化分辨率控件

            # 隐藏本机鼠标
            self.Checkbutton_HideLocalMouse_IntVar = tk.IntVar()
            self.Checkbutton_HideLocalMouse_IntVar.set(g_iHideLocalMouse)
            self.Checkbutton_HideLocalMouse = tk.Checkbutton(
                self,
                text='隐藏本机鼠标',
                onvalue=1,
                offvalue=0,
                variable=self.Checkbutton_HideLocalMouse_IntVar,
                command=self.Fun_SetHideLocalMouse)
            if g_iMousePositionMethod == 2:
                self.Checkbutton_HideLocalMouse.config(state='disable')
            self.Checkbutton_HideLocalMouse.pack()
            # 隐藏本机鼠标

            self.deiconify()
            DialogCenter(self)

        def Fun_SetHideLocalMouse(self):
            global g_iHideLocalMouse
            g_iHideLocalMouse = self.Checkbutton_HideLocalMouse_IntVar.get()
            if g_iHideLocalMouse:
                VideoControl.config(cursor='none')
            else:
                VideoControl.config(cursor='')
            Fun_SetStatusBar()

        def Fun_Combobox_Resolution_Selected(self, event):
            iIndex = self.Combobox_Resolution.current()
            if iIndex < len(g_ResolutionTable):
                g_iWidth, g_iHeight = g_ResolutionTable[iIndex][0], g_ResolutionTable[iIndex][1]
                Fun_SetScreenResolution(g_iWidth, g_iHeight)
                Fun_SetStatusBar()

    except Exception:
        pass


def Fun_Setup(WindowRoot):
    DialogSetup(WindowRoot)


def Fun_SetStatusBar():
    strState = '隐藏' if g_iHideLocalMouse else '显示'
    if g_iMousePositionMethod == 2:
        strState = '隐藏'
    strData = '【目标设备屏幕分辨率：%d x %d】 \\ 【本机鼠标指针状态：%s】 \\ 【图像采集卡设备序号：%d】 \\ 【键鼠控制器设备名：%s】' % \
        (g_iWidth, g_iHeight, strState, g_iVideoDeviceIndex, g_strSerialDeviceName)
    if g_iMousePositionMethod == 2:
        strMousePromptRc = '按Ctrl + Alt + Space组合键释放鼠标' if g_MouseHasBeenCaptured else '点击鼠标按键方可捕获鼠标'
        strMousePrompt = ' \\ 【★★%s★★】' % strMousePromptRc
        strData += strMousePrompt

    StatusBar.config(text=strData)


def Fun_GrabScreen():
    global g_GrabScreen
    g_GrabScreen = True


if __name__ == '__main__':
    strVersion = '1.2'
    Fun_LoadConfigFile()

    try:
        Window = tk.Tk()
        Window.withdraw()
        if platform.system().lower() == 'windows':
            try:
                Window.iconbitmap('resource/%s.ico' % g_strProgramName)
            except Exception:
                pass
        strWindowTitle = '%s v%s' % (
            g_strProgramName + ' 软件', strVersion)
        Window.title(strWindowTitle)
        Window.resizable(False, False)

        try:
            g_serial_com = serial.Serial(
                g_strSerialDeviceName, 57600, 8, 'N', 1, timeout=10)
            if g_serial_com.is_open is False:
                messagebox.showerror(title=g_strProgramName + ' 软件',
                                     message='打开USB HID设备失败，请检查配置文件是否配置正确。')
                Fun_SaveConfigFile()
                sys.exit()
        except Exception:
            messagebox.showerror(title=g_strProgramName + ' 软件',
                                 message='打开USB HID设备失败，请检查配置文件是否配置正确。')
            Fun_SaveConfigFile()
            sys.exit()

        # 菜单
        MainMenu = tk.Menu(Window)
        MainMenu.add_command(label="设置", command=lambda: Fun_Setup(Window))
        MainMenu_Keyboard = tk.Menu(MainMenu, tearoff=False)
        MainMenu.add_cascade(label="发送键盘按键", menu=MainMenu_Keyboard)
        MainMenu_Keyboard.add_command(
            label="Ctrl + Alt + Del", command=lambda: Fun_WriteSerial('[K0500630000000000][K0000000000000000]'))
        MainMenu_Keyboard.add_command(
            label="Ctrl + Shift + Esc", command=lambda: Fun_WriteSerial('[K0300290000000000][K0000000000000000]'))
        MainMenu_Keyboard.add_command(
            label="Alt + F4", command=lambda: Fun_WriteSerial('[K04003D0000000000][K0000000000000000]'))
        MainMenu_Keyboard.add_command(
            label="Alt + Tab", command=lambda: Fun_WriteSerial('[K04002B0000000000][K0000000000000000]'))
        MainMenu_Keyboard.add_command(
            label="Win", command=lambda: Fun_WriteSerial('[K0800000000000000][K0000000000000000]'))
        MainMenu.add_command(label="捕获屏幕", command=Fun_GrabScreen)
        Window.config(menu=MainMenu)
        # 菜单
        VideoControl = tk.Canvas(Window, width=g_iWidth,
                                 height=g_iHeight, bg='white', bd=-1)

        VideoControl.pack()

        # 状态栏
        StatusBar = tk.Label(Window, text='', bd=1,
                             relief=tk.SUNKEN, anchor=tk.W)
        StatusBar.pack(side=tk.BOTTOM, fill=tk.X)
        StatusBar.focus_set()
        Fun_SetStatusBar()
        # 状态栏

        Window.bind('<Key>', Fun_Callback_Keyboard)  # 键盘
        VideoControl.bind('<Button-1>', Fun_Callback_Mouse_Button)  # 鼠标左键单击
        VideoControl.bind('<Button-2>', Fun_Callback_Mouse_Button)  # 鼠标中键单击
        VideoControl.bind('<Button-3>', Fun_Callback_Mouse_Button)  # 鼠标右键单击
        VideoControl.bind('<ButtonRelease-1>',
                          Fun_Callback_Mouse_ButtonRelease)  # 鼠标左键释放
        VideoControl.bind('<ButtonRelease-2>',
                          Fun_Callback_Mouse_ButtonRelease)  # 鼠标中键释放
        VideoControl.bind('<ButtonRelease-3>',
                          Fun_Callback_Mouse_ButtonRelease)  # 鼠标右键释放
        VideoControl.bind('<MouseWheel>', Fun_Callback_Mouse_Wheel)  # 鼠标滚轮
        VideoControl.bind('<Enter>', Fun_Callback_Mouse_Enter)
        VideoControl.bind('<Leave>', Fun_Callback_Mouse_Leave)

        # 点击界面右上角的关闭按钮时，会触发'WM_DELETE_WINDOW'消息
        # 我们在此截获该消息，并改变其行为
        Window.protocol('WM_DELETE_WINDOW', Fun_CloseWindow)

        Window.after(500, Fun_ShowVideo)
        Window.eval('tk::PlaceWindow . center')
        Window.mainloop()

    except Exception as e:
        Fun_WriteLog(str(e))
