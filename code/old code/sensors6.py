import sys
import time
import statistics
from collections import deque

sys.path.insert(0, '/home/pi/bob/lib/python3.11/site-packages')

from smbus2 import SMBus
import serial


ser = serial.Serial('/dev/serial0', 115200, timeout=0)

REAR_I2C_ADDR = 0x10


class Luna:
    def __init__(self, ser, bus_id=1, rear_i2c_addr=0x10, history_size=5):
        self.ser = ser
        self.bus = SMBus(bus_id)
        self.REAR_I2C_ADDR = rear_i2c_addr
        self.rear_hist = deque(maxlen=history_size)

    def _median_or_none(self, values):
        if not values:
            return None
        return int(statistics.median(values))

    def read_rear_i2c(self):
        try:
            data = self.bus.read_i2c_block_data(self.REAR_I2C_ADDR, 0x00, 2)
            if len(data) < 2:
                return None

            distance = data[0] | (data[1] << 8)
            self.rear_hist.append(distance)
            return self._median_or_none(self.rear_hist)

        except OSError:
            return None

    def read_tf_luna(self):
        if self.ser.in_waiting >= 9:
            bytes_serial = self.ser.read(9)
            self.ser.reset_input_buffer()

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:
                distance = bytes_serial[2] + (bytes_serial[3] << 8)
                return distance

        return None

    def get_distance_front(self):
        return self.read_tf_luna()

    def get_distance(self):
        rear = self.read_rear_i2c()
        front = self.get_distance_front()
        map_size = 300

        if front is not None and rear is not None:
            if front + rear == map_size:
                return front

        if front is None or front == 0:
            if rear is not None and rear != 0:
                return map_size - rear

        if front is None and rear is None:
            print("both sensors are not online")
            return None

        return front

    def close(self):
        if hasattr(self, "bus") and self.bus is not None:
            self.bus.close()
            self.bus = None
        if hasattr(self, "ser") and self.ser is not None:
            self.ser.close()
            self.ser = None


class scans:
    luna = Luna(ser)

    @staticmethod
    def lidar_scan():
        return scans.luna.get_distance()

    @staticmethod
    def full_scan():
        while True:
            print("lidar:", scans.lidar_scan())
            time.sleep(0.1)


if __name__ == "__main__":
    try:
        scans.full_scan()
    except KeyboardInterrupt:
        print("Stopping...")
        scans.luna.close()