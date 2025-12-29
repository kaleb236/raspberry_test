import asyncio
import websockets
import json
from roboclaw_3 import Roboclaw
import math


speed = {
    "linear_x": 0.0,
    "angular_z": 0.0
}
# -----------------------
# Roboclaw setup
# -----------------------
rc = Roboclaw("/dev/ttyACM0", 115200)
rc.Open()
address = 0x80

CPR = 2048

max_speed = 50000  # default max speed

def set_motors(x, z):
    print("sending motor, x:", x, " z:", z)
    rpm_l, rpm_r = speed_to_rpm(x, z, 0.033, 0.16)

    left_tick = int(rpm_l * CPR / 60)
    right_tick = int(rpm_r * CPR / 60)

    print(f"Left ticks: {left_tick}, Right ticks: {right_tick}")

    rc.SpeedM1M2(address, left_tick, right_tick)


def speed_to_rpm(v, omega, r, L):
    v_l = v - (L / 2.0) * omega
    v_r = v + (L / 2.0) * omega

    omega_l = v_l / r
    omega_r = v_r / r

    rpm_l = omega_l * 60 / (2 * math.pi)
    rpm_r = omega_r * 60 / (2 * math.pi)

    return [rpm_l, rpm_r]

# -----------------------
# WebSocket handler (single argument)
# -----------------------
async def handler(websocket):
    global max_speed
    async for message in websocket:
        try:
            data = json.loads(message)
            set_motors(data["linear_x"], data["angular_z"])
        except Exception as e:
            print("Error processing message:", e)

# -----------------------
# Start server
# -----------------------
async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket server running on ws://0.0.0.0:8765")
        await asyncio.Future()  # keep running

if __name__ == "__main__":
    asyncio.run(main())
