try:
    from smbus2 import SMBus
except ModuleNotFoundError:
    print("Smbus2 is not installed. \nMake sure to runining: pip install smbus2 \nOr make sure you are running on a virtual machine.")
    exit()    
import time

addr = 0x8 # bus address
bus = SMBus(1) # indicates /dev/ic2-1
start = time.time()
for n in range(1000):
    try:
        bus.write_i2c_block_data(addr, 48, [] )
    except OSError:
        print("OSError could not send",n)
    time.sleep(0.03)
end = time.time()
print((end - start)/1000)

