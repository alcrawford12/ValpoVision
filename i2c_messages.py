try:
    from smbus2 import SMBus
except ImportError:
    print("Smbus2 is not installed. \nMake sure to runining: pip install smbus2 \nOr make sure you are running on a virtual machine.")
    exit()
    
class i2c_messages():
    def __init__(self,addr,bus_number,suppress_errors = True):
        self.addr = addr
        self.bus = SMBus(bus_number)
        self.suppress_errors = suppress_errors
    def write_array(self, array):
        try:
            self.bus.write_i2c_block_data(self.addr, array[0], array[1:-1] )
        except OSError:
            print("OSError could not send")
"""Example class

message = i2c_messages(addr = 0x8, # bus address,
                       bus_number = 1,# indicates /dev/ic2-1,
                       suppress_errors = False #optional
                       )
message.write_array([2,3])

"""

