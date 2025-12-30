from roboclaw_3 import Roboclaw
import time
rc = Roboclaw("/dev/ttyACM0", 115200)
rc.Open()
address = 0x80
# rc.DutyM1(address, 10000)
# time.sleep(1)
# rc.DutyM1(address, -10000)
rc.SpeedM1(address, 14190)
time.sleep(1)
rc.DutyM1M2(address, 0, 0)