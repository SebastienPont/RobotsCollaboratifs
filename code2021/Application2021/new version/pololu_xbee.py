from digi.xbee.devices import RemoteXBeeDevice, XBeeDevice
from digi.xbee.models.address import XBee64BitAddress
import time

# pour la communication
'''
On a: 1/gfd  2/grt  3/glf  4/stp  5/rdy 6/ 7/
'''
device = None

class XbeeApp(object):

    def __init__(self):
        self.remote_device_1 = None
        self.Init = 0
        self.address = "0013A20041BAEAD6"

    @staticmethod
    def init_port(Com, Baud):
        global device
        device = XBeeDevice(Com, Baud)
        device.open()

    @staticmethod
    def end_com():
        global device
        device.close()

    def init_device(self, Address):
        self.remote_device_1 = RemoteXBeeDevice(device, \
            XBee64BitAddress.from_hex_string(Address))
        self.Init = 1

    def send_msg(self,Msg = "non"):
        if(self.Init != 1):
            print("Faut initialiser")
            return 0
        else:
            device.send_data_async(self.remote_device_1, Msg)

    def func_test_1(self):
        time.sleep(1.0)
        device.send_data_async(self.remote_device_1, "rdy")
        print("rdy")
        time.sleep(3.0)

        device.send_data_async(self.remote_device_1, "gfd")
        print("gfd")
        time.sleep(2.0)

        device.send_data_async(self.remote_device_1, "grt")
        print("grt")
        time.sleep(0.5)

        device.send_data_async(self.remote_device_1, "gfd")
        print("grt")
        time.sleep(2.0)

        device.send_data_async(self.remote_device_1, "stp")
        print("stp")
        time.sleep(1.0)
