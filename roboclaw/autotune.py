from roboclaw_3 import Roboclaw

rc = Roboclaw("/dev/ttyACM0", 115200)
rc.Open()
address = 0x80
rc.AutoTuneM1Velocity(address, 8000, 20)
# print("EEPROM Data at address 0x80:", result)