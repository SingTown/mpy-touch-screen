import struct
import time
class Touch:
    def __init__(self,spi,cs):
        self.spi = spi
        self.cs = cs
    def _read(self,cmd):
        self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        time.sleep_us(4)
        data = (struct.unpack('>H',self.spi.read(2))[0]>>3)&0xFFF
        self.cs.value(1)
        return data
    def raw_read(self):
        return self._read(0x90), self._read(0xD0)#x,y
    def read_xy(self):
        self.spi.init(baudrate = 2000000)
        x_list=[]
        y_list=[]
        for i in range(5):
            coor = self.raw_read()
            x_list.append(coor[0])
            y_list.append(coor[1])
        self.spi.init(baudrate = 80000000)
        if max(x_list) == 0xFFF or min(y_list) == 0x0:
            return (None,None)
        else:
            x_list.sort()
            y_list.sort()
            
            x=sum(x_list[1:-1])//3
            y=sum(y_list[1:-1])//3
            return x,y
