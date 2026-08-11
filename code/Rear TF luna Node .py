import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import smbus2


class TfLunaRearI2C(Node):
    def __init__(self):
        super().__init__('tf_luna_rear_i2c')

        self.publisher_ = self.create_publisher(Float32, '/tf_luna/rear/distance', 10)

        self.declare_parameter('i2c_bus', 1)
        self.declare_parameter('i2c_addr', 0x10)

        bus_num = self.get_parameter('i2c_bus').value
        self.addr = self.get_parameter('i2c_addr').value

        self.bus = smbus2.SMBus(bus_num)
        self.timer = self.create_timer(0.1, self.read_and_publish)

    def read_distance_cm(self):
        data = self.bus.read_i2c_block_data(self.addr, 0x00, 2)
        distance_cm = data[0] + (data[1] << 8)
        return distance_cm

    def read_and_publish(self):
        try:
            distance_cm = self.read_distance_cm()

            msg = Float32()
            msg.data = float(distance_cm) / 100.0
            self.publisher_.publish(msg)

            self.get_logger().info(f'rear distance={msg.data:.2f} m')

        except Exception as e:
            self.get_logger().error(f'I2C read failed: {e}')

    def destroy_node(self):
        try:
            if hasattr(self, 'bus'):
                self.bus.close()
        finally:
            super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = TfLunaRearI2C()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()