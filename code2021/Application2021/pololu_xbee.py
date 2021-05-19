from digi.xbee.devices import RemoteXBeeDevice, XBeeDevice
from digi.xbee.models.address import XBee64BitAddress
import time

# pour la communication
'''
On a: 1/gfd  2/grt  3/glf  4/stp  5/rdy 6/ 7/
'''

class Xbee_app(object):

    def __init__(self):
        self.device = None
        self.remote_device_1 = None
        self.Init = 0

    def Init_device(self):
        self.device = XBeeDevice("COM25", 9600)
        self.device.open()
        self.remote_device_1 = RemoteXBeeDevice(self.device, \
            XBee64BitAddress.from_hex_string("0013A20041BAEAD6"))
        self.Init = 1

    def Send_Msg(self,Msg = "non"):
        if(self.Init != 1):
            print("Faut initialiser")
            return 0
        else:
            self.device.send_data_async(self.remote_device_1, Msg)

    def Func_test_1(self):
        time.sleep(1.0)
        self.device.send_data_async(self.remote_device_1, "rdy")
        print("rdy")
        time.sleep(3.0)

        self.device.send_data_async(self.remote_device_1, "gfd")
        print("gfd")
        time.sleep(2.0)

        self.device.send_data_async(self.remote_device_1, "grt")
        print("grt")
        time.sleep(0.5)

        self.device.send_data_async(self.remote_device_1, "gfd")
        print("grt")
        time.sleep(2.0)

        self.device.send_data_async(self.remote_device_1, "stp")
        print("stp")
        time.sleep(1.0)

    def End_com(self):
        self.device.close()