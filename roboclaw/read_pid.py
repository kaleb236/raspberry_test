from roboclaw_3 import Roboclaw

rc = Roboclaw("/dev/ttyACM0", 115200)
rc.Open()
address = 0x80
result = rc.ReadM1VelocityPID(address)
result2 = rc.ReadM2VelocityPID(address)
print("M2 Velocity PID:", result2)
print("M1 Velocity PID:", result)