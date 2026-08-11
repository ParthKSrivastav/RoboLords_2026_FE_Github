
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32

import serial


class TFLunaFront(Node):

    def __init__(self):
        super().__init__('tf_luna_front')


        # ---------------- Parameters ----------------

        self.declare_parameter(
            'port',
            '/dev/ttyS0'
        )

        self.declare_parameter(
            'baudrate',
            115200
        )


        port = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value


        # ---------------- Serial ----------------

        try:

            self.ser = serial.Serial(
                port,
                baudrate,
                timeout=0.1
            )

            self.get_logger().info(
                f"TF-Luna connected on {port}"
            )


        except Exception as e:

            self.get_logger().error(
                f"Could not open TF-Luna: {e}"
            )

            raise



        # ---------------- Publisher ----------------

        self.publisher_ = self.create_publisher(
            Float32,
            '/tf_luna/front',
            10
        )


        # ---------------- Timer ----------------

        self.timer = self.create_timer(
            0.01,
            self.read_and_publish
        )


        # ---------------- Debug counter ----------------

        self.log_counter = 0


        self.get_logger().info(
            "Front TF-Luna node started"
        )



    def read_frame(self):

        try:

            while self.ser.in_waiting >= 9:

                frame = self.ser.read(9)


                # Header check

                if frame[0] != 0x59 or frame[1] != 0x59:
                    continue



                # Checksum

                checksum = sum(frame[:8]) & 0xFF


                if checksum != frame[8]:

                    self.get_logger().warning(
                        "TF-Luna checksum error"
                    )

                    return None



                # Decode packet

                distance_cm = (
                    frame[2]
                    + (frame[3] << 8)
                )


                strength = (
                    frame[4]
                    + (frame[5] << 8)
                )


                temperature = (
                    frame[6]
                    + (frame[7] << 8)
                ) / 8.0 - 256



                return (
                    distance_cm,
                    strength,
                    temperature
                )


        except Exception as e:

            self.get_logger().error(
                f"Read frame error: {e}"
            )


        return None



    def read_and_publish(self):

        try:

            result = self.read_frame()


            if result is None:
                return



            distance_cm, strength, temperature = result



            # ---------- Debug logging ----------
            
            self.log_counter += 1


            if self.log_counter % 20 == 0:

                self.get_logger().info(
                    f"Front TF-Luna | "
                    f"Distance: {distance_cm} cm | "
                    f"Strength: {strength} | "
                    f"Temp: {temperature:.1f}"
                )



            # ---------- Publish ----------

            msg = Float32()

            # metres for ROS convention

            msg.data = float(distance_cm) / 100.0


            self.publisher_.publish(msg)



        except Exception as e:

            self.get_logger().error(
                f"TF-Luna publish failed: {e}"
            )



    def destroy_node(self):

        try:

            if self.ser.is_open:
                self.ser.close()

        except:
            pass


        super().destroy_node()



def main(args=None):

    rclpy.init(args=args)


    node = TFLunaFront()


    try:

        rclpy.spin(node)


    except KeyboardInterrupt:

        pass



    node.destroy_node()

    rclpy.shutdown()



if __name__ == '__main__':
    main()