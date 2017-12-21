import time
import os
import ustruct
import gc
#import basecolor
import math

class ILI9341:
    def __init__(self, spi, cs=None, dc=None, rst=None, backled=None, width=320, height=240,
                 bcolor=0x00):
        self.width = width
        self.height = height
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.backled = backled
        self.reset()
        self.init()
        #self.font = font()
        #self.font_size = list(self.font.font_lib.keys())
        self.backcolor = bcolor
        self.clear(self.backcolor)
        # self._scroll = 0

    ####################################################################################
    def brightness(self, brightness):
        self.backled.duty(brightness)

    def init(self):
        for command, data in (
                (0xef, b'\x03\x80\x02'),
                (0xcf, b'\x00\xc1\x30'),
                (0xed, b'\x64\x03\x12\x81'),
                (0xe8, b'\x85\x00\x78'),
                (0xcb, b'\x39\x2c\x00\x34\x02'),
                (0xf7, b'\x20'),
                (0xea, b'\x00\x00'),
                (0xc0, b'\x23'),  # Power Control 1, VRH[5:0]
                (0xc1, b'\x10'),  # Power Control 2, SAP[2:0], BT[3:0]
                (0xc5, b'\x3e\x28'),  # VCM Control 1
                (0xc7, b'\x86'),  # VCM Control 2
                (0x36, b'\x28'),  # Memory Access Control
                (0x3a, b'\x66'),  # Pixel Format
                (0xb1, b'\x00\x18'),  # FRMCTR1
                (0xb6, b'\x08\x82\x27'),  # Display Function Control
                (0xf2, b'\x00'),  # 3Gamma Function Disable
                (0x26, b'\x01'),  # Gamma Curve Selected
                (0xe0, b'\x0f\x31\x2b\x0c\x0e\x08\x4e\xf1\x37\x07\x10\x03\x0e\x09\x00'),  # Set Gamma
                (0xe1, b'\x00\x0e\x14\x03\x11\x07\x31\xc1\x48\x08\x0f\x0c\x31\x36\x0f'),  # Set Gamma
        ):
            self.write(command, data)
        self.write(0x11)
        time.sleep_ms(120)
        self.write(0x29)

    def reset(self):
        self.rst(0)
        time.sleep_ms(50)
        self.rst(1)
        time.sleep_ms(50)
    ####################################################################################
    def write(self, command=None, data=None):
        if command:
            self.dc(0)
            self.cs(0)
            self.spi.write(bytearray([command]))
            self.cs(1)
        if data:
            self.dc(1)
            self.cs(0)
            self.spi.write(data)
            self.cs(1)
    def read(self, command=None, count=None):
        self.dc(0)
        self.cs(0)
        if command is None:
            pass
        else:
            self.spi.write(bytearray([command]))
        if count is None:
            pass
        else:
            data = self.spi.read(count)
            self.cs(1)
            return data
        return b''
    ################################################################################
    def send_coor(self,x,y,w,h):
        self.write(command=0x2a, data=ustruct.pack('>HH', x, x+w-1))
        self.write(command=0x2b, data=ustruct.pack('>HH', y, y+h-1))
        self.write(command=0x2c)
    ################################################################################
    def pixel(self, x, y, color=0xffffff):  # 在x,y处画一个color颜色的点
        self.send_coor(x,y,1,1)
        self.write(data=color)

    def rect(self, x, y, w, h, color=0xffffff):
        self.send_coor(x,y,w,h)
        a = w * h // 512
        for i in range(a):
            self.write(data=color.to_bytes(3,'big')*512)
        gc.collect()

    ################################################################################
    def line(self, x, y, x1, y1, thickness=1, color=0xffffff):  # 画线
        pass

    def box(self, x, y, width, height, color, is_fill=False, angle=0):  # 方框，is_fill is true 填充
        pass

    def circle(self, x, y, r, color, is_fill=False):
        pass

    def clear(self, color=0xffffff):
        data=color.to_bytes(3,'big')*320*3
        for i in range(40):
            self.send_coor(0,3*(40-i-1),self.width,3)
            self.write(data=data)
            self.send_coor(0,3*(40+i),self.width,3)
            self.write(data=data)

    ################################################################################

    def display_ppm(self, path,x,y):
        if path.split('.')[-1] != 'ppm':
            print('image format is not support!')
            return -1
        with open(path, 'rb') as img:
            head = img.readline().decode().strip().upper()
            if head != 'P6':
                print('head not support! head:', head)
            width = int(img.readline())
            height = int(img.readline())
            max_pix = int(img.readline())
            self.send_coor(x,y,width,height)

            a, b = divmod(width * height * 3, 1024)
            if a > 0:
                for i in range(a):
                    temp = img.read(1024)
                    self.write(data=temp)
            if b > 0:
                temp = img.read(b)
                self.write(data=temp)
            del temp
            gc.collect()
    
