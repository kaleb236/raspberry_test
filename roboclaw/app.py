import asyncio
import websockets
import json
from roboclaw_3 import Roboclaw

# -----------------------
# Roboclaw setup
# -----------------------
rc = Roboclaw("/dev/ttyACM0", 115200)
rc.Open()
address = 0x80

max_speed = 50000  # default max speed

def set_motors(left, right):
    print("sending motor")
    left = max(min(int(left), 127), -127)
    right = max(min(int(right), 127), -127)

    left_speed = int(left / 127 * max_speed)
    right_speed = int(right / 127 * max_speed)

    rc.SpeedM1M2(address, left_speed, right_speed)

# -----------------------
# WebSocket handler (single argument)
# -----------------------
async def handler(websocket):
    global max_speed
    async for message in websocket:
        try:
            data = json.loads(message)
            if "left" in data and "right" in data:
                set_motors(data["left"], data["right"])
            if "speed" in data:
                max_speed = int(data["speed"])
                print(f"Max speed set to {max_speed}")
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
