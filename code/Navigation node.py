    #!/usr/bin/env python3
## this is our current code for both open and obstacle it starts with imports, then defining all the variables, then subscribing to sensor info (kind of like subscribingto a youtube channel it gets information from the sensors)
# THe code then makes the functions for camera, turning and moving forward
#then it makes the navigation loop and stopping code
# then creates the main 

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
        # Navigation node initialization
        # -----------------------------

        super().__init__("navigation_node")

        self.imu_restarting = False
        self.declare_parameter("mode", "OPEN")

        # -----------------------------
        # Turn tracking
        # -----------------------------
        self.lap = 0 
        self.turn_count = 0
        self.turning = False
        self.turn_start_yaw = None

        # -----------------------------
        # IMU recovery
        # -----------------------------

        self.last_good_yaw = 0.0

        # -----------------------------
        # Camera values
        # -----------------------------

        self.green_detected = False
        self.green_x = -1.0

        self.red_detected = False
        self.red_x = -1.0

        # -----------------------------
        # Obstacle state
        # -----------------------------

        self.obstacle_state = "NONE"
        self.obstacle_direction = None
        self.obstacle_start_yaw = None
        self.obstacle_target_yaw = None

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
        # Camera subscribers
        # -----------------------------

        self.green_sub = self.create_subscription(
            Bool,
            "/camera/green_detected",
            self.green_callback,
            10
        )

        self.green_x_sub = self.create_subscription(
            Float32,
            "/camera/green_x",
            self.green_x_callback,
            10
        )

        self.red_sub = self.create_subscription(
            Bool,
            "/camera/red_detected",
            self.red_callback,
            10
        )

        self.red_x_sub = self.create_subscription(
            Float32,
            "/camera/red_x",
            self.red_x_callback,
            10
        )

        # -----------------------------
        # Heading control
        # -----------------------------

        self.yaw = 0.0
        self.filtered_yaw = 0.0
        self.target_yaw = None

        # Gyro filter strength
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

        self.drive_speed = 0.15

        self.turn_speed = 0.70
        self.turn_throttle = 0.30

        # P controller gain
        self.kp = 0.025

        # Maximum steering
        self.max_steering = 0.60

        # -----------------------------
        # Obstacle settings
        # -----------------------------

        self.obstacle_turn_speed = 0.60
        self.obstacle_drive_speed = 0.15

        # Distance at which obstacle is considered passed.
        # CHANGE THIS AFTER TESTING.
        self.obstacle_clear_distance = 1.00

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
    # Camera callbacks
    # =================================================

    def green_callback(self, msg):
        self.green_detected = msg.data

    def green_x_callback(self, msg):
        self.green_x = msg.data

    def red_callback(self, msg):
        self.red_detected = msg.data

    def red_x_callback(self, msg):
        self.red_x = msg.data

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
    # IMU restart callback
    # =================================================

    def imu_restart_callback(self, msg):

        self.imu_restarting = msg.data

        if msg.data:

            # Save the last known good heading
            self.last_good_yaw = self.yaw

            self.get_logger().warn(
                f"IMU restarting. "
                f"Last good yaw = {self.last_good_yaw:.1f}"
            )

    # =================================================
    # IMU callback
    # =================================================

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

        raw_yaw = self.normalize_angle(raw_yaw)

        # Low-pass filter

        difference = self.normalize_angle(
            raw_yaw - self.filtered_yaw
        )

        self.filtered_yaw += (
            self.filter_alpha * difference
        )

        self.filtered_yaw = self.normalize_angle(
            self.filtered_yaw
        )

        self.yaw = self.normalize_angle(
            self.filtered_yaw
        )

        # If this is a normal valid IMU reading,
        # remember it as the last good yaw.

        if not self.imu_restarting:

            self.last_good_yaw = self.yaw

        self.get_logger().debug(
            f"Raw: {raw_yaw:.2f} "
            f"Filtered: {self.yaw:.2f}"
        )

        # Store starting heading

        if self.target_yaw is None:

            self.target_yaw = self.yaw

            self.get_logger().info(
                f"Starting heading: "
                f"{self.target_yaw:.1f} degrees"
            )

    # =================================================
    # Camera / colour detection
    # =================================================

    def colour_detection(self):

        # Do not detect another obstacle while
        # already performing an avoidance manoeuvre.

        if self.obstacle_state != "NONE":
            return

        # -----------------------------
        # GREEN -> RIGHT
        # -----------------------------

        if (
            self.green_detected
            and 150 < self.green_x < 400
        ):

            self.obstacle_direction = "RIGHT"

            self.obstacle_start_yaw = self.yaw

            self.obstacle_target_yaw = (
                self.normalize_angle(
                    self.obstacle_start_yaw + 45.0
                )
            )

            self.obstacle_state = "TURN_OUT"

            self.get_logger().info(
                f"GREEN -> RIGHT | "
                f"Start={self.obstacle_start_yaw:.1f} | "
                f"Target={self.obstacle_target_yaw:.1f}"
            )

        # -----------------------------
        # RED -> LEFT
        # -----------------------------

        elif (
            self.red_detected
            and 150 < self.red_x < 400
        ):

            self.obstacle_direction = "LEFT"

            self.obstacle_start_yaw = self.yaw

            self.obstacle_target_yaw = (
                self.normalize_angle(
                    self.obstacle_start_yaw - 45.0
                )
            )

            self.obstacle_state = "TURN_OUT"

            self.get_logger().info(
                f"RED -> LEFT | "
                f"Start={self.obstacle_start_yaw:.1f} | "
                f"Target={self.obstacle_target_yaw:.1f}"
            )

    # =================================================
    # Obstacle navigation
    # =================================================

    def obstacle_logic(self):

        if self.obstacle_state == "NONE":
            return False

        command = Twist()

        # =================================================
        # TURN OUT 45 DEGREES
        # =================================================

        if self.obstacle_state == "TURN_OUT":

            error = self.normalize_angle(
                self.obstacle_target_yaw - self.yaw
            )

            # 3 degree tolerance
            if abs(error) <= 3.0:

                self.obstacle_state = "PASS"

                self.get_logger().info(
                    "Obstacle 45 degree turn complete."
                )

                return True

            command.linear.x = self.turn_throttle

            if error > 0:
                command.angular.z = self.obstacle_turn_speed
            else:
                command.angular.z = -self.obstacle_turn_speed

            self.motor_pub.publish(command)

            return True

        # =================================================
        # PASS THE OBSTACLE
        # =================================================

        if self.obstacle_state == "PASS":

            command.linear.x = self.obstacle_drive_speed
            command.angular.z = 0.0

            self.motor_pub.publish(command)

            # Once the front sensor sees enough
            # space, begin returning to original heading.

            if self.front_distance >= self.obstacle_clear_distance:

                self.obstacle_target_yaw = (
                    self.obstacle_start_yaw
                )

                self.obstacle_state = "TURN_BACK"

                self.get_logger().info(
                    f"Obstacle passed. "
                    f"Returning to heading "
                    f"{self.obstacle_start_yaw:.1f}"
                )

            return True

        # =================================================
        # TURN BACK TO ORIGINAL HEADING
        # =================================================

        if self.obstacle_state == "TURN_BACK":

            error = self.normalize_angle(
                self.obstacle_target_yaw - self.yaw
            )

            if abs(error) <= 3.0:

                self.obstacle_state = "NONE"

                self.obstacle_direction = None
                self.obstacle_start_yaw = None
                self.obstacle_target_yaw = None

                self.target_yaw = self.yaw

                self.get_logger().info(
                    "Obstacle manoeuvre complete. "
                    "Returning to normal navigation."
                )

                return True

            command.linear.x = self.turn_throttle

            if error > 0:
                command.angular.z = self.obstacle_turn_speed
            else:
                command.angular.z = -self.obstacle_turn_speed

            self.motor_pub.publish(command)

            return True

        return False

    # =================================================
    # Normal 90 degree turn logic
    # =================================================

    def turn_logic(self, target_angle=80.0):

        if not self.turning:
            return

        angle_turned = self.normalize_angle(
            self.yaw - self.turn_start_yaw
        )

        # Normal 80 degree completion
        # OR early completion if LiDAR sees enough space
        if (
            abs(angle_turned) >= target_angle
            or
            (self.front_distance > 1.25 and abs(angle_turned) >= 65.0)
        ):
            self.stop_robot()
            self.turning = False

            # Count the completed turn
            self.turn_count += 1

            self.target_yaw = self.yaw

            self.get_logger().info(
                f"Turn completed. "
                f"Turn angle: {angle_turned:.1f} degrees. "
                f"Total turns: {self.turn_count}/4"
            )

            # ---------------------------------
            # LAP COMPLETE AFTER 4 TURNS
            # ---------------------------------

            if self.turn_count >= 4:

                self.lap += 1
                self.turn_count = 0

                self.get_logger().info(
                    f"========== LAP COMPLETED =========="
                )

                self.get_logger().info(
                    f"Total laps: {self.lap}/3"
                )

            self.get_logger().info(
                f"New target yaw: {self.target_yaw:.1f}"
            )
    # =================================================
    # Normal driving
    # =================================================

    def move_forward(self):

        command = Twist()

        # -----------------------------
        # Normal Open Challenge turn
        # -----------------------------

        if self.front_distance < 0.75:

            self.turning = True

            self.turn_start_yaw = self.yaw

            self.get_logger().info(
                f"Turn started at "
                f"{self.turn_start_yaw:.1f} degrees"
            )

            command.linear.x = self.turn_throttle
            command.angular.z = self.turn_speed

            self.motor_pub.publish(command)

            return

        # -----------------------------
        # Straight driving
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
    # Main navigation loop
    # =================================================

    def navigation_loop(self):
        
        if self.lap > 3:
            self.stop_robot()
            return
        # -----------------------------
        # IMU restart = STOP
        # -----------------------------
        if self.imu_restarting:
            self.yaw = self.last_good_yaw
            self.filtered_yaw = self.last_good_yaw

            command = Twist()
            command.linear.x = 0.0
            command.angular.z = 0.0

            self.motor_pub.publish(command)
            return

        # -----------------------------
        # Wait for first IMU heading
        # -----------------------------

        if self.target_yaw is None:
            return

        # -----------------------------
        # If currently doing a normal turn
        # -----------------------------

        if self.turning:

            self.turn_logic(80.0)

            if self.turning:
                self.get_logger().info(
                    f"Turning at "
                    f"{self.front_distance:.1f} degrees"
                )
                command = Twist()

                command.linear.x = self.turn_throttle
                command.angular.z = self.turn_speed

                self.motor_pub.publish(command)

            return

        # -----------------------------
        # OBSTACLE MODE
        # -----------------------------

        if self.mode == "OBSTACLE":

            # Look for a new obstacle
            if self.obstacle_state == "NONE":
                self.colour_detection()

            # Execute obstacle manoeuvre
            if self.obstacle_state != "NONE":
                self.obstacle_logic()
                return

        # -----------------------------
        # Normal driving
        # -----------------------------

        self.move_forward()

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
