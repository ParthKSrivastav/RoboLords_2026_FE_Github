#!/usr/bin/env python3
import sys
sys.path.append("/home/pi/bob/lib/python3.11/site-packages")
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

from gpiozero import Motor


class Robot:
    def __init__(self, driving, steering):
        self.driving = driving
        self.steering = steering

    def set_throttle(self, speed):
        speed = max(-1.0, min(1.0, speed))

        if speed > 0:
            self.driving.forward(speed)
        elif speed < 0:
            self.driving.backward(abs(speed))
        else:
            self.driving.stop()

    def set_steering(self, steering):
        steering = max(-1.0, min(1.0, steering))

        if steering > 0:
            self.steering.forward(steering)
        elif steering < 0:
            self.steering.backward(abs(steering))
        else:
            self.steering.stop()

    def stop(self):
        self.driving.stop()
        self.steering.stop()


class MotorNode(Node):

    def __init__(self):
        super().__init__('motor_node')

        # CHANGE THESE GPIO PINS
        driving_motor = Motor(
            forward=17,
            backward=27
        )

        steering_motor = Motor(
            forward=22,
            backward=23
        )

        self.robot = Robot(driving_motor, steering_motor)

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_callback,
            10
        )

        self.get_logger().info("Motor node started.")

    def cmd_callback(self, msg):

        throttle = msg.linear.x
        steering = msg.angular.z

        self.robot.set_throttle(throttle)
        self.robot.set_steering(steering)

        self.get_logger().info(
            f"Throttle={throttle:.2f} Steering={steering:.2f}"
        )

    def destroy_node(self):
        self.robot.stop()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = MotorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.robot.stop()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()