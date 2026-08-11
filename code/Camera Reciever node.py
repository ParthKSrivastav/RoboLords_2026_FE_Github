#!/usr/bin/env python3

import socket

import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool, Float32


class CameraReceiver(Node):

    def __init__(self):
        super().__init__("camera_receiver")

        # -----------------------------
        # ROS publishers
        # -----------------------------

        self.green_pub = self.create_publisher(
            Bool,
            "/camera/green_detected",
            10
        )

        self.green_x_pub = self.create_publisher(
            Float32,
            "/camera/green_x",
            10
        )

        self.red_pub = self.create_publisher(
            Bool,
            "/camera/red_detected",
            10
        )

        self.red_x_pub = self.create_publisher(
            Float32,
            "/camera/red_x",
            10
        )

        # -----------------------------
        # TCP server
        # -----------------------------

        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server.bind(
            ("0.0.0.0", 5000)
        )

        self.server.listen(1)

        self.get_logger().info(
            "Camera receiver waiting on port 5000..."
        )

        # This accepts the camera connection.
        # For now this is fine because there is
        # only one camera.
        self.connection, self.address = self.server.accept()

        self.get_logger().info(
            f"Camera connected: {self.address}"
        )

        # -----------------------------
        # Buffer
        # -----------------------------

        self.buffer = ""

        # -----------------------------
        # Receive timer
        # -----------------------------

        self.timer = self.create_timer(
            0.01,
            self.receive_data
        )

        self.get_logger().info(
            "Camera receiver started."
        )

    # =================================================
    # Receive TCP data
    # =================================================

    def receive_data(self):

        try:

            data = self.connection.recv(1024)

            if not data:
                self.get_logger().warn(
                    "Camera disconnected."
                )
                return

            self.buffer += data.decode()

            # TCP does not guarantee that one recv()
            # equals one complete message.
            #
            # We therefore process complete lines.
            while "\n" in self.buffer:

                line, self.buffer = self.buffer.split(
                    "\n",
                    1
                )

                line = line.strip()

                if line:
                    self.process_data(line)

        except Exception as e:

            self.get_logger().error(
                f"TCP error: {e}"
            )

    # =================================================
    # Process camera data
    # =================================================

    def process_data(self, line):

        try:

            values = line.split(",")

            if len(values) != 4:
                self.get_logger().warn(
                    f"Invalid camera data: {line}"
                )
                return

            green = bool(int(values[0]))
            green_x = float(values[1])

            red = bool(int(values[2]))
            red_x = float(values[3])

            # -----------------------------
            # Publish green
            # -----------------------------

            green_msg = Bool()
            green_msg.data = green

            self.green_pub.publish(
                green_msg
            )

            green_x_msg = Float32()
            green_x_msg.data = green_x

            self.green_x_pub.publish(
                green_x_msg
            )

            # -----------------------------
            # Publish red
            # -----------------------------

            red_msg = Bool()
            red_msg.data = red

            self.red_pub.publish(
                red_msg
            )

            red_x_msg = Float32()
            red_x_msg.data = red_x

            self.red_x_pub.publish(
                red_x_msg
            )

            # Debug output
            self.get_logger().debug(
                f"Green={green} "
                f"X={green_x:.0f} | "
                f"Red={red} "
                f"X={red_x:.0f}"
            )

        except Exception as e:

            self.get_logger().error(
                f"Failed to parse camera data "
                f"'{line}': {e}"
            )

    # =================================================
    # Shutdown
    # =================================================

    def destroy_node(self):

        self.get_logger().info(
            "Stopping camera receiver..."
        )

        try:
            self.connection.close()
        except Exception:
            pass

        try:
            self.server.close()
        except Exception:
            pass

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = CameraReceiver()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()