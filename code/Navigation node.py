#!/usr/bin/env python3

import math
import rclpy

from rclpy.node import Node

from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
from std_msgs.msg import Bool

class NavigationNode(Node):

    def __init__(self):
# -----------------------------
# Turn tracking
# -----------------------------
        super().__init__("navigation_node")
        self.imu_restarting = False
# -----------------------------
# Turn tracking
# -----------------------------
        #start_yaw = self.yaw
        self.turn_count = 0
        self.turning = False
        self.turn_start_yaw = None

        # -----------------------------
        # Publisher to motor node
        # -----------------------------

        self.motor_pub = self.create_publisher(
            Twist,
            "/cmd_vel",
            10
        )


        # -----------------------------
        # IMU subscriber
        # -----------------------------

        self.imu_sub = self.create_subscription(
            Imu,
            "/imu/data",
            self.imu_callback,
            10
        )
        self.imu_restart_sub = self.create_subscription(
            Bool,
            "/imu/restart",
            self.imu_restart_callback,
            10
        )

        # -----------------------------
        # TF-Luna subscribers
        # -----------------------------

        self.front_distance = 999.0
        self.rear_distance = 999.0


        self.front_sub = self.create_subscription(
            Float32,
            "/tf_luna/front",
            self.front_callback,
            10
        )


        self.rear_sub = self.create_subscription(
            Float32,
            "/tf_luna/rear",
            self.rear_callback,
            10
        )


        # -----------------------------
        # Heading control
        # -----------------------------

        self.yaw = 0.0
        #self.filtered_yaw = 0.0
        # IMU filtering
        self.filtered_yaw = 0.0
        #self.filter_alpha = 0.15
        self.target_yaw = None


        # Gyro filter strength
        # Lower = smoother but slower response
        self.filter_alpha = 0.15

        # -----------------------------
        # Lap tracking
        # -----------------------------

        self.lap = 1
        self.mode = "LAP_1"
        self.lap_marker_locked = False

        # -----------------------------
        # Driving settings
        # -----------------------------

        self.drive_speed = 0.30
        self.turn_speed = 0.50
        self.turn_throttle = 0.50
        # P controller gain
        self.kp = 0.025

        # Maximum steering
        self.max_steering = 0.60



        # -----------------------------
        # Navigation loop
        # -----------------------------

        self.timer = self.create_timer(
            0.05,
            self.navigation_loop
        )


        self.get_logger().info(
            "Navigation node started."
        )


    # =================================================
    # Angle helper
    # =================================================

    def normalize_angle(self, angle):

        while angle > 180:
            angle -= 360

        while angle < -180:
            angle += 360

        return angle



    # =================================================
    # TF-Luna callbacks
    # =================================================

    def front_callback(self, msg):

        self.front_distance = msg.data



    def rear_callback(self, msg):

        self.rear_distance = msg.data



    # =================================================
    # IMU callback
    # =================================================
    def imu_restart_callback(self, msg):
        self.imu_restarting = msg.data



    def imu_callback(self, msg):

        x = msg.orientation.x
        y = msg.orientation.y
        z = msg.orientation.z
        w = msg.orientation.w
    
    
        # Quaternion -> yaw
    
        siny_cosp = 2.0 * (w * z + x * y)
    
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    
    
        yaw_rad = math.atan2(
            siny_cosp,
            cosy_cosp
        )
    
    
        raw_yaw = math.degrees(yaw_rad)
    
    
        # Normalize raw angle first
        raw_yaw = self.normalize_angle(raw_yaw)
    
    
        # Low pass filter
# Calculate shortest angle difference
        difference = self.normalize_angle(
            raw_yaw - self.filtered_yaw
        )
        
        # Apply filter
        self.filtered_yaw += (
            self.filter_alpha * difference
        )
        
        # Keep angle between -180 and 180
        self.filtered_yaw = self.normalize_angle(
            self.filtered_yaw
        )
            
            
        self.yaw = self.normalize_angle(
            self.filtered_yaw
        )
    
    
        self.get_logger().debug(
            f"Raw: {raw_yaw:.2f} Filtered: {self.yaw:.2f}"
        )
    
    
        # Store starting heading
    
        if self.target_yaw is None:
    
            self.target_yaw = self.yaw
    
            self.get_logger().info(
                f"Starting heading: {self.target_yaw:.1f} degrees"
            )
    
    def turn_logic(self):
        
        if not self.turning:
            return

        angle_turned = self.normalize_angle(
            self.yaw - self.turn_start_yaw
        )

        if abs(angle_turned) >= 90.0:

            self.turning = False
            self.turn_count += 1

            # New heading becomes the straight-driving target
            self.target_yaw = self.yaw

            self.get_logger().info(
                f"Turn completed. "
                f"Turn angle: {angle_turned:.1f} degrees. "
                f"Total turns: {self.turn_count}"
            )

            self.get_logger().info(
                f"New target yaw: {self.target_yaw:.1f}"
            )




    def lap_logic(self):
        if self.lap == 1:
            self.mode = "LAP_1"
            pass
        elif self.lap == 2:
            self.mode = "LAP_2"
            pass
        elif self.lap == 3:
            self.mode = "LAP_3"
            pass
    
        # =================================================
        # Main navigation loop
        # =================================================

    def navigation_loop(self):
        #start_yaw = self.yaw
        
        if self.imu_restarting:
            command = Twist()
            command.linear.x = 0.0
            command.angular.z = 0.0
            self.motor_pub.publish(command)
            return

        if self.target_yaw is None:
            return

        command = Twist()

        # -----------------------------
        # If currently turning
        # -----------------------------

        if self.turning:
            self.turn_logic()

            if self.turning:
                command.linear.x = self.turn_throttle
                command.angular.z = self.turn_speed

                self.motor_pub.publish(command)
                return

               
        # -----------------------------
        # Start a new turn
        # -----------------------------

        if self.front_distance < 0.50:

            self.turning = True
            self.turn_start_yaw = self.yaw

            self.get_logger().info(
                f"Turn started at {self.turn_start_yaw:.1f} degrees"
            )

            command.linear.x = self.turn_throttle
            command.angular.z = self.turn_speed

            self.motor_pub.publish(command)
            return

        # -----------------------------
        # Normal driving
        # -----------------------------

        error = self.normalize_angle(
            self.target_yaw - self.filtered_yaw
        )

        if abs(error) < 2.0:
            error = 0.0

        steering = -self.kp * error

        steering = max(
            -self.max_steering,
            min(self.max_steering, steering)
        )

        command.linear.x = self.drive_speed
        command.angular.z = steering

        self.motor_pub.publish(command)
    # =================================================
    # Stop robot
    # =================================================

    def stop_robot(self):

        command = Twist()

        command.linear.x = 0.0
        command.angular.z = 0.0

        self.motor_pub.publish(command)



# =================================================
# Main
# =================================================

def main(args=None):

    rclpy.init(args=args)

    node = NavigationNode()


    try:

        rclpy.spin(node)


    except KeyboardInterrupt:

        node.get_logger().info(
            "Stopping navigation"
        )

        node.stop_robot()


    finally:

        node.destroy_node()

        rclpy.shutdown()



if __name__ == "__main__":

    main()