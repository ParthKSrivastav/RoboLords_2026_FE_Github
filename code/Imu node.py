
#!/usr/bin/env python3

import sys
import time

sys.path.append("/home/pi/bob/lib/python3.11/site-packages")

import rclpy
from rclpy.node import Node

from adafruit_extended_bus import ExtendedI2C

from sensor_msgs.msg import Imu
from std_msgs.msg import Bool

from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import BNO_REPORT_GAME_ROTATION_VECTOR


class IMUNode(Node):

    def __init__(self):
        super().__init__("imu_node")

        # -------------------------------------------------
        # State
        # -------------------------------------------------

        self.gyro_restart = False

        # -------------------------------------------------
        # BNO085
        # -------------------------------------------------

        self.i2c = ExtendedI2C(3)

        self.bno = BNO08X_I2C(
            self.i2c,
            debug=False
        )

        self.bno.enable_feature(
            BNO_REPORT_GAME_ROTATION_VECTOR
        )

        self.get_logger().info(
            "BNO085 initialised."
        )

        # -------------------------------------------------
        # Publishers
        # -------------------------------------------------

        self.publisher = self.create_publisher(
            Imu,
            "/imu/data",
            10
        )

        self.restart_pub = self.create_publisher(
            Bool,
            "/imu/restart",
            10
        )

        # -------------------------------------------------
        # Timer
        # 50 Hz
        # -------------------------------------------------

        self.timer = self.create_timer(
            0.02,
            self.publish_imu
        )

        self.get_logger().info(
            "IMU node started."
        )

    # =================================================
    # Publish restart state
    # =================================================

    def publish_restart_state(self):

        msg = Bool()
        msg.data = self.gyro_restart

        self.restart_pub.publish(msg)

    # =================================================
    # Restart BNO085
    # =================================================

    def restart_imu(self):

        self.gyro_restart = True
        self.publish_restart_state()

        self.get_logger().warn(
            "BNO085 failure detected. "
            "Robot should STOP."
        )

        # -------------------------------------------------
        # Try three times
        # -------------------------------------------------

        for attempt in range(1, 4):

            self.get_logger().warn(
                f"BNO085 restart attempt "
                f"{attempt}/3"
            )

            # Give the sensor time to recover
            time.sleep(0.5)

            try:

                # Recreate I2C connection
                self.i2c = ExtendedI2C(3)

                # Recreate BNO085 object
                self.bno = BNO08X_I2C(
                    self.i2c,
                    debug=False
                )

                # Re-enable quaternion output
                self.bno.enable_feature(
                    BNO_REPORT_GAME_ROTATION_VECTOR
                )

                # Give the sensor a short time
                # to begin producing data
                time.sleep(0.2)

                # -------------------------------------------------
                # Successful recovery
                # -------------------------------------------------

                self.get_logger().info(
                    "BNO085 restarted successfully."
                )

                self.gyro_restart = False
                self.publish_restart_state()

                return True

            except Exception as e:

                self.get_logger().error(
                    f"BNO085 restart attempt "
                    f"{attempt}/3 failed: {e}"
                )

        # -------------------------------------------------
        # Recovery failed
        # -------------------------------------------------

        self.gyro_restart = True
        self.publish_restart_state()

        self.get_logger().error(
            "BNO085 could not be recovered "
            "after 3 attempts."
        )

        self.get_logger().error(
            "Robot must remain STOPPED."
        )

        return False

    # =================================================
    # IMU callback
    # =================================================

    def publish_imu(self):

        # -------------------------------------------------
        # Do not attempt normal IMU publishing while
        # recovery is already in progress.
        # -------------------------------------------------

        if self.gyro_restart:
            return

        try:

            q = self.bno.game_quaternion

            if q is None:
                return

            # -------------------------------------------------
            # Create IMU message
            # -------------------------------------------------

            msg = Imu()

            msg.header.stamp = (
                self.get_clock()
                .now()
                .to_msg()
            )

            msg.header.frame_id = "imu_link"

            # BNO085 returns:
            # x, y, z, w

            msg.orientation.x = q[0]
            msg.orientation.y = q[1]
            msg.orientation.z = q[2]
            msg.orientation.w = q[3]

            # -------------------------------------------------
            # Publish quaternion
            # -------------------------------------------------

            self.publisher.publish(msg)

            # -------------------------------------------------
            # Debug output
            # -------------------------------------------------

            self.get_logger().info(
                f"Quaternion: "
                f"x={q[0]:.3f}, "
                f"y={q[1]:.3f}, "
                f"z={q[2]:.3f}, "
                f"w={q[3]:.3f}"
            )

        except Exception as e:

            error_text = str(e)

            self.get_logger().error(
                f"IMU read error: {error_text}"
            )

            # -------------------------------------------------
            # Only recover from known communication failures
            # -------------------------------------------------

            if (
                "Errno 5" in error_text
                or "Unprocessable Batch bytes" in error_text
            ):

                # Prevent another recovery attempt from
                # starting while one is already active.
                if not self.gyro_restart:

                    self.restart_imu()

            else:

                # Unknown error:
                # do not automatically restart the sensor.
                self.get_logger().error(
                    "Unknown IMU error. "
                    "No automatic restart performed."
                )


# =================================================
# Main
# =================================================

def main(args=None):

    rclpy.init(args=args)

    node = IMUNode()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        node.get_logger().info(
            "Stopping IMU node."
        )

    finally:

        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
```