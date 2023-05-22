# -*- coding: utf-8 -*-

g_KeyValueTable = [  # 键盘编码映射定义关系[Windows系统keycode定义码, 0x0左侧按键 | 0x1右侧按键, VNC keycode定义码, HID设备定义码]
    [0x41, 0x0, 0x26, 0x04],      # A
    [0x42, 0x0, 0x27, 0x05],      # B
    [0x43, 0x0, 0x28, 0x06],      # C
    [0x44, 0x0, 0x29, 0x07],      # D
    [0x45, 0x0, 0x2A, 0x08],      # E
    [0x46, 0x0, 0x2B, 0x09],      # F
    [0x47, 0x0, 0x2C, 0x0A],      # G
    [0x48, 0x0, 0x2D, 0x0B],      # H
    [0x49, 0x0, 0x2E, 0x0C],      # I
    [0x4A, 0x0, 0x2F, 0x0D],      # J
    [0x4B, 0x0, 0x30, 0x0E],      # K
    [0x4C, 0x0, 0x31, 0x0F],      # L
    [0x4D, 0x0, 0x32, 0x10],      # M
    [0x4E, 0x0, 0x33, 0x11],      # N
    [0x4F, 0x0, 0x34, 0x12],      # O
    [0x50, 0x0, 0x35, 0x13],      # P
    [0x51, 0x0, 0x36, 0x14],      # Q
    [0x52, 0x0, 0x37, 0x15],      # R
    [0x53, 0x0, 0x38, 0x16],      # S
    [0x54, 0x0, 0x39, 0x17],      # T
    [0x55, 0x0, 0x3A, 0x18],      # U
    [0x56, 0x0, 0x3B, 0x19],      # V
    [0x57, 0x0, 0x3C, 0x1A],      # W
    [0x58, 0x0, 0x3D, 0x1B],      # X
    [0x59, 0x0, 0x3E, 0x1C],      # Y
    [0x5A, 0x0, 0x3F, 0x1D],      # Z
    [0x31, 0x0, 0x12, 0x1E],      # 1
    [0x32, 0x0, 0x13, 0x1F],      # 2
    [0x33, 0x0, 0x14, 0x20],      # 3
    [0x34, 0x0, 0x15, 0x21],      # 4
    [0x35, 0x0, 0x16, 0x22],      # 5
    [0x36, 0x0, 0x17, 0x23],      # 6
    [0x37, 0x0, 0x18, 0x24],      # 7
    [0x38, 0x0, 0x19, 0x25],      # 8
    [0x39, 0x0, 0x1A, 0x26],      # 9
    [0x30, 0x0, 0x11, 0x27],      # 0
    [0x0D, 0x0, 0x41, 0x28],      # ENTER
    [0x1B, 0x0, 0x43, 0x29],      # ESC
    [0x08, 0x0, 0x40, 0x2A],      # Backspace
    [0x09, 0x0, 0x42, 0x2B],      # TAB
    [0x20, 0x0, 0x10, 0x2C],      # SPACE 空格
    [0xBD, 0x0, 0x1B, 0x2D],      # - 横杠以及下划线
    [0xBB, 0x0, 0x1C, 0x2E],      # = 等号与加号
    [0xDB, 0x0, 0x1D, 0x2F],      # [ 左中括号与大括号
    [0xDD, 0x0, 0x1E, 0x30],      # ] 右中括号与大括号
    [0xDC, 0x0, 0x25, 0x31],      # \ |
    [0xBA, 0x0, 0x1F, 0x33],      # ; : 分号和冒号
    [0xDE, 0x0, 0x20, 0x34],      # ‘ “ 单引号和双引号
    [0xC0, 0x0, 0x21, 0x35],      # ` ~ (数字键 1 左边的那个键)
    [0xBC, 0x0, 0x22, 0x36],      # , < 逗号和小于号
    [0xBE, 0x0, 0x23, 0x37],      # . > 句号和大于号
    [0xBF, 0x0, 0x24, 0x38],      # / ? 斜杠与问号
    [0x14, 0x0, 0x59, 0x39],      # Capslock 大小写锁定
    [0x70, 0x0, 0x4D, 0x3A],      # F1
    [0x71, 0x0, 0x4E, 0x3B],      # F2
    [0x72, 0x0, 0x4F, 0x3C],      # F3
    [0x73, 0x0, 0x50, 0x3D],      # F4
    [0x74, 0x0, 0x51, 0x3E],      # F5
    [0x75, 0x0, 0x52, 0x3F],      # F6
    [0x76, 0x0, 0x53, 0x40],      # F7
    [0x77, 0x0, 0x54, 0x41],      # F8
    [0x78, 0x0, 0x55, 0x42],      # F9
    [0x79, 0x0, 0x56, 0x43],      # F10
    [0x7A, 0x0, 0x57, 0x44],      # F11
    [0x7B, 0x0, 0x58, 0x45],      # F12
    [0x00, 0x0, 0x5E, 0x46],      # Printscreen 【Windows未捕获】
    [0x91, 0x0, 0x00, 0x47],      # Scroll lock 【VNC未捕获】
    [0x13, 0x0, 0x5F, 0x48],      # Pause
    [0x2D, 0x1, 0x60, 0x49],      # Insert
    [0x24, 0x1, 0x45, 0x4A],      # Home
    [0x21, 0x1, 0x47, 0x4B],      # Pageup
    [0x2E, 0x1, 0x44, 0x4C],      # DELETE
    [0x23, 0x1, 0x46, 0x4D],      # End
    [0x22, 0x1, 0x48, 0x4E],      # Pagedown
    [0x27, 0x1, 0x4C, 0x4F],      # Rightarrow →
    [0x25, 0x1, 0x4B, 0x50],      # Leftarrow ←
    [0x28, 0x1, 0x4A, 0x51],      # Downarrow ↓
    [0x26, 0x1, 0x49, 0x52],      # Uparrow ↑
    [0x90, 0x1, 0x61, 0x53],      # Num lock
    [0x6F, 0x1, 0x62, 0x54],      # 小键盘 /
    [0x6A, 0x0, 0x63, 0x55],      # 小键盘 *
    [0x6D, 0x0, 0x64, 0x56],      # 小键盘 -
    [0x6B, 0x0, 0x65, 0x57],      # 小键盘 +
    [0x0D, 0x1, 0x66, 0x58],      # 小键盘 Enter
    [0x61, 0x0, 0x5B, 0x59],      # 小键盘 1
    [0x62, 0x0, 0x5C, 0x5A],      # 小键盘 2
    [0x63, 0x0, 0x72, 0x5B],      # 小键盘 3
    [0x64, 0x0, 0x74, 0x5C],      # 小键盘 4
    [0x65, 0x0, 0x75, 0x5D],      # 小键盘 5
    [0x66, 0x0, 0x76, 0x5E],      # 小键盘 6
    [0x67, 0x0, 0x71, 0x5F],      # 小键盘 7
    [0x68, 0x0, 0x77, 0x60],      # 小键盘 8
    [0x69, 0x0, 0x73, 0x61],      # 小键盘 9
    [0x60, 0x0, 0x5A, 0x62],      # 小键盘 0
    [0x6E, 0x0, 0x5D, 0x63],      # 小键盘 . DELETE
    [0x5D, 0x1, 0x78, 0x65],      # Application，右 GUI (Win) 与 CTRL 之间
    [0x00, 0x0, 0x00, 0x66],      # 其它特殊-Power 【未捕获】
    [0x00, 0x0, 0x00, 0x74],      # 其它特殊-Execute 【未捕获】
    [0x00, 0x0, 0x00, 0x75],      # 其它特殊-Help 【未捕获】
    [0x00, 0x0, 0x00, 0x76],      # 其它特殊-Menu 【未捕获】
    [0x00, 0x0, 0x00, 0x77],      # 其它特殊-Select 【未捕获】
    [0x00, 0x0, 0x00, 0x78],      # 其它特殊-Stop 【未捕获】
    [0x00, 0x0, 0x00, 0x79],      # 其它特殊-Again 【未捕获】
    [0x00, 0x0, 0x00, 0x7A],      # 其它特殊-Undo 【未捕获】
    [0x00, 0x0, 0x00, 0x7B],      # 其它特殊-Cut 【未捕获】
    [0x00, 0x0, 0x00, 0x7C],      # 其它特殊-Copy 【未捕获】
    [0x00, 0x0, 0x00, 0x7D],      # 其它特殊-Paste 【未捕获】
    [0x00, 0x0, 0x00, 0x7E],      # 其它特殊-Find 【未捕获】
    [0x00, 0x0, 0x00, 0x7F],      # 其它特殊-Mute 【未捕获】
    [0x00, 0x0, 0x00, 0x80],      # 其它特殊-Volmue Up 【未捕获】
    [0x00, 0x0, 0x00, 0x81],      # 其它特殊-Volmue Down 【未捕获】
    [0x11, 0x0, 0x08, 0xE0],      # L CTRL
    [0x10, 0x0, 0x0A, 0xE1],      # L SHIFT
    [0x12, 0x0, 0x0E, 0xE2],      # L ALT
    [0x5B, 0x0, 0x79, 0xE3],      # L GUI (Win)
    [0x10, 0x1, 0x09, 0xE4],      # R CTRL
    [0x11, 0x1, 0x0A, 0xE5],      # R SHIFT
    [0x12, 0x1, 0x0F, 0xE6],      # R ALT
    [0x5B, 0x1, 0x00, 0xE7]       # R GUI (Win) 【VNC未捕获】
]