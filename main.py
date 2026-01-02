import websockets
import os
import asyncio
import subprocess
import math
import json
from roboclaw.roboclaw_3 import Roboclaw
from sensors import battery, mesafe, led_test
from audio_test import record_audio

class SystemController:
    def __init__(self):
        self.rc = Roboclaw("/dev/ttyACM0", 115200)
        self.rc.Open()
        self.address = 0x80

        self.led_controller = led_test.LEDController(spi_bus=0, spi_device=0, led_count=100)

        try:
            self.rc.ReadVersion(self.address)
        except Exception as e:
            print("Roboclaw initialization error:", e)
        try:
            self.battery = battery.INA219(addr=0x41)
        except Exception as e:
            print("Battery sensor initialization error:", e)
            self.battery = None
    
    def __speed_to_rpm(self, v, omega, r, L):
        v_l = v - (L / 2.0) * omega
        v_r = v + (L / 2.0) * omega

        omega_l = v_l / r
        omega_r = v_r / r

        rpm_l = omega_l * 60 / (2 * math.pi)
        rpm_r = omega_r * 60 / (2 * math.pi)

        return [rpm_l, rpm_r]
    
    def __set_motors(self, x, z):
        print("sending motor, x:", x, " z:", z)
        rpm_l, rpm_r = self.__speed_to_rpm(x * -1, z, 0.0553, 0.169)

        left_tick = int(rpm_l * CPR / 60)
        right_tick = int(rpm_r * CPR / 60)

        print(f"Left ticks: {left_tick}, Right ticks: {right_tick}")
        #rc.SpeedM2(address, left_tick)
        self.rc.SpeedM1M2(address, left_tick, right_tick * -1)
    
    def __play_sound(self, path):
        print("Playing sound:", path)
        subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    async def sender(self, websocket):
        while True:
            bus_voltage = self.batter.getBusVoltage_V() if self.battery else 0
            shunt_voltage = self.batter.getShuntVoltage_mV() / 1000 if self.battery else 0
            current = self.batter.getCurrent_mA() if self.battery else 0
            power = self.batter.getPower_W() if self.battery else 0
            p = (bus_voltage - 9)/3.6*100
            if(p > 100):p = 100
            if(p < 0):p = 0

            try:
                with mesafe.SMBus(mesafe.I2C_BUS) as bus:
                    mesafe_distance = mesafe.read_distance_mm(bus)
            except Exception as e:
                print("Mesafe sensor read error:", e)
                mesafe_distance = 0
            data = {
                "bus_voltage": bus_voltage,
                "shunt_voltage": shunt_voltage,
                "current": current,
                "power": power,
                "percent": p,
                "mesafe_distance": mesafe_distance
            }
            await websocket.send(json.dumps(data))
            await asyncio.sleep(0.05)

    async def receiver(self, websocket):
        print("Client connected")
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                command_type = data.get("type")
                if command_type == "motor":
                    self.__set_motors(data["data"]["linear_x"], data["data"]["angular_z"])
                elif command_type == "led":
                    self.led_controller.set_color(data["data"]["r"], data["data"]["g"], data["data"]["b"])
                elif command_type == "mic":
                    record_audio.start_recording()
                elif command_type == "speaker":
                    if os.path.exists("mic_recording_boosted.wav"):
                        self.__play_sound("mic_recording_boosted.wav")
                    else:
                        await websocket.send(json.dumps({"error": "Audio file not found"}))

        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
    
    async def handler(self, websocket):
        sender_task = asyncio.create_task(self.sender(websocket))
        receiver_task = asyncio.create_task(self.receiver(websocket))
        done, pending = await asyncio.wait(
            [sender_task, receiver_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()

async def main():
    system_controller = SystemController()
    async with websockets.serve(system_controller.handler, "0.0.0.0", 8080):
        print("WebSocket server running on :8080")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())