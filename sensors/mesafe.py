import time
from smbus2 import SMBus

# VL53L0X default I2C address
VL53L0X_ADDR = 0x29
I2C_BUS = 1

# Important registers
SYSRANGE_START = 0x00
RESULT_RANGE_STATUS = 0x14

def read_distance_mm(bus):
    # Start single ranging measurement
    bus.write_byte_data(VL53L0X_ADDR, SYSRANGE_START, 0x01)

    # Wait for measurement to complete
    time.sleep(0.03)

    # Read result registers
    data = bus.read_i2c_block_data(VL53L0X_ADDR, RESULT_RANGE_STATUS, 12)

    # Distance is stored in bytes 10 & 11
    distance = (data[10] << 8) | data[11]
    return distance


def main():
    with SMBus(I2C_BUS) as bus:
        print("VL53L0X initialized")

        while True:
            try:
                distance = read_distance_mm(bus)
                print(f"Range: {distance} mm")
                time.sleep(0.1)
            except OSError as e:
                print("I2C error:", e)
                time.sleep(1)


if __name__ == "__main__":
    main()
