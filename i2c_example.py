from i2c_messages import *


message = i2c_messages(addr = 0x8, # bus address,
                       bus_number = 1,# indicates /dev/ic2-1,
                       suppress_errors = False #optional
                       )
message.write_array([2,3])
