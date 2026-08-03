print("testing v4")
#######
import sys
sys.path.insert(0, '/home/pi/bob/lib/python3.11/site-packages')
import adafruit_mpu6050
import board
import busio 
import serial
import cv2
import numpy as np
from picamera2 import Picamera2
import threading
ser = serial.Serial("/dev/serial0", 115200, timeout=0)
luna = sensors6.Luna(ser,bus_id=1)
global current_seen
current_seen = "None"
####################################################################################CAMERA CODE#####################################################################################################
# Start camera
def camera():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"format": "RGB888", "size": (640, 480)}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)

# HSV ranges
# Green
    lower_green = np.array([35, 80, 80])
    upper_green = np.array([85, 255, 255])

# Red needs two ranges because HSV hue wraps around
    lower_red1 = np.array([0, 80, 80])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 80, 80])
    upper_red2 = np.array([179, 255, 255])

    while True:
        frame = picam2.capture_array()

    # Convert RGB to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

    # Masks
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    # Clean up masks
        kernel = np.ones((5, 5), np.uint8)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
        global current_seen
        current_seen = "None"
    # Find contours for green
        green_contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in green_contours:
            global Object
            Object = True
        
            current_seen = "green"
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "GREEN", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Find contours for red
        red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in red_contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, "RED", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow("Color Detection", frame)
        cv2.imshow("Red Mask", red_mask)
        cv2.imshow("Green Mask", green_mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
#
    cv2.destroyAllWindows()
    picam2.stop()
def colour_detection():
    robot = Robot()
    print("entered colour detection")
    global current_seen
    while True:
        print("scanning in the loop")
        global current_seen
        if current_seen == "green":
            print("Green object detected!")
            robot.luna_turn_45_right()
            robot.drive_forward(speed=0.2)
            robot.wait(timeout=0.5)
            robot.luna_turn_45_left()
            robot.luna_turn_45_left()
            robot.drive_forward(speed=0.2)
            robot.wait(timeout=0.5)
            
        else:
            print("red object detected.")
            robot.luna_turn_45_left()
            robot.drive_forward(speed=0.2)
            robot.wait(timeout=0.5)
            robot.luna_turn_45_right()
            robot.luna_turn_45_right()
            robot.drive_forward(speed=0.2)
            robot.wait(timeout=0.5)
        time.sleep(0.5)  # Adjust the sleep time as needed
#######################################ROBOT~##################################################################################

class Robot:
    def __init__(self):
        self.driving  = Motor(17, 18)
        self.steering = Motor(22, 23)
    def drive_forward(self, speed=0.5):
        self.driving.forward(speed=0.3)


    def stop(self):
        self.driving.stop()
        self.steering.stop()

    def move_forward(self, speed=1.0, distance_target=100):
        global Object
        Object = True
        global current_seen
        colour_detection()
        dist  = luna.get_distance()
        print("Starting move_forward â†’ target distance: " + str(dist) + " cm")
        start = time.time()
        while dist >= distance_target:
            self.drive_forward(speed)
            dist = luna.get_distance()
        self.stop()

    def turn_right(self, speed=0.5):
        self.steering.forward(speed=speed)
        
    def turn_left(self, speed=0.5):
        self.steering.backward(speed=speed)
        
    def move_backward(self, speed=0.5):
        self.driving.backward(speed=speed)
    def stop(self):
        self.driving.stop()
        self.steering.stop()
        self.wait(timeout=0.1)
    def wait(self, timeout=1):
        try:
            time.sleep(timeout)
        except:
            pass
    def stop_steering(self):
        self.steering.stop()
        self.wait(timeout=0.1)

    def keep_straight_right(self):
        self.stop_steering()
        self.turn_left(speed=0.3)
        self.wait(timeout=0.13)
        self.stop_steering()
    def keep_straight_left(self):
        self.stop_steering()
        self.turn_right(speed=0.3)
        self.wait(timeout=0.13)
        self.stop_steering()
#############################################################LUNA TURN LOGIC#####################################################################################################
    def luna_turn(self):
         self.steering.forward(speed=0.8)
         time.sleep(1.0)
         #'
         #
         timeout=0.0
         while timeout <= 10.0:
            self.driving.forward(0.8)
            timeout += 0.1  
            #print("gyro value z " + str(sensors6.mpu.gyro[1])+ " gyro value y " + str(sensors6.mpu.gyro[0]) + " gyro value x " + str(sensors6.mpu.gyro[2]))
            print(f"Turning... LiDAR distance: {luna.get_distance()} cm" + str(timeout) + " timer" )#
            time.sleep(0.01)  # small delay to avoid excessive polling
            
         self.stop()
         self.keep_straight_right()  # optional: straighten after turn
    #print("gyroangle = " + str(sensors5.gyro_sensor.get_yaw()) + "Â°")p(
    # def _get_yaw_corrected(self):
    #     raw = sensors5.gyro_sensor.get_yaw()
    #     if abs(raw) < 0.05: 
    #         return 0.0
    #     return raw#
    def luna_turn_45_right(self):
        self.steering.forward(speed=0.8)
        time.sleep(0.5)
        timeout=0.0
        while timeout <= 10.0:
            self.driving.forward(0.8)
            timeout += 0.1  
            print(f"Turning... LiDAR distance: {luna.get_distance()} cm" + str(timeout) + " timer" )#
            time.sleep(0.01)  # small delay to avoid excessive polling
            
        self.stop()
        self.keep_straight_right()  # optional: straighten after turn


    def luna_turn_45_left(self):
        self.steering.backward(speed=0.8)
        time.sleep(0.5)
        timeout=0.0
        while timeout <= 10.0:
            self.driving.forward(0.8)
            timeout += 0.1  
            print(f"Turning... LiDAR distance: {luna.get_distance()} cm" + str(timeout) + " timer" )#
            time.sleep(0.01)  # small delay to avoid excessive polling
            
        self.stop()
        self.keep_straight_left()  # optional: straighten after turn
    def luna_turn_left(self):
        global Object
        Object = False
        self.sterering.backward(speed=0.8)
        while timeout <= 10.0:
            self.driving.forward(0.4)
            timeout += 0.1  
            print(f"Turning... LiDAR distance: {luna.get_distance()} cm" + str(timeout) + " timer" )#
            time.sleep(0.01)  # small delay to avoid excessive polling
  
        
        timeout = 0.0 
        self.keep_straight_left()  

 
#############################################################LAP LOGIC#####################################################################################################

    def move_in_lap(self, forward_speed=0.5, turn_speed=0.8,
                    distance_target=100, turn_angle=90, laps=0):
        laps_completed = 0
        while laps_completed <= 3:
            print(f"  Lap {laps_completed + 1} of {laps}")
            self.move_forward(speed=forward_speed, distance_target=distance_target)
            self.luna_turn()
            print("turn 1 complete")
            self.move_forward(speed=forward_speed, distance_target=distance_target)
            self.luna_turn()
            print("turn 2 complete")
            self.move_forward(speed=forward_speed, distance_target=distance_target)
            self.luna_turn()
            print("turn 3 complete")
            self.move_forward(speed=forward_speed, distance_target=distance_target)
            self.luna_turn()
            print("turn 4 complete")
            laps_completed += 1
            print(f" Lap {laps_completed}/{laps} complete")

        print(" All laps complete!")


    def move_in_lap_left(self, forward_speed=0.5, turn_speed=0.8,
                    distance_target=100, turn_angle=90, target_turns=12):
        global turns
        laps_completed = 0 
        print("object is not detected robot is moving")
        
        while laps_completed <= 3:
            
            print("turn 1 complete")
            
            self.move_forward(speed=forward_speed, distance_target=distance_target)
            self.luna_turn_left()
            print("turn 2 complete")
            
            self.move_forward(speed=forward_speed, distance_target=distance_target)
            self.luna_turn_left()
            print("turn 3 complete")
            
            self.move_forward(speed=forward_speed, distance_target=distance_target)
            self.luna_turn_left()
            print("turn 4 complete")
            laps_completed += 1
        print("\nâœ“ All laps complete!")

##################################################################OTHER FUNCTIONS#####################################################################################################

def button_code():
    print("code is starting and button has pressed")
    global turns
    t3 = threading.Thread(target=colour_detection)
    t1 = threading.Thread(target=camera)
    t2 = threading.Thread(target=coin_flip)
    print("t1 starting")
    t1.start()
    t2.start()
    print("starting t3")
    t1.join()
    t3.join()

def coin_flip():
    dist = luna.get_distance()
    robot.camera_turn_left(speed=0.5)
    if dist < 64:
        print("robot continues turning left")  
        robot.camera_turn_left(speed=0.5)
        robot.move_in_lap_left(forward_speed=0.5, turn_speed=0.8,
                    distance_target=100, turn_angle=90, target_turns=12)
    elif dist > 64:
        print("robot continues turning right")
        robot.camera_turn_right(speed=0.5)
        robot.move_in_lap(forward_speed=0.5, turn_speed=0.8,
                    distance_target=100, turn_angle=90, laps=3)

##########################################################MAIN###################################################################################
if __name__ == "__main__":
    robot = Robot()
    print("code is starting up...")
    distance = luna.get_distance()
    print(str(distance) + " cm")
    button_code()
    


