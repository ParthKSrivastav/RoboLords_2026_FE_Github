print("final version ")
import time
import sys
sys.path.insert(0,'/home/pi/bob/lib/python3.11/site-packages')
from gpiozero import Motor, Button

import sensors6
import time
import time
import threading 
from signal import pause
import time
from gpiozero import Button
ser = serial.Serial("/dev/serial0", 115200, timeout=0)
luna = sensors6.Luna(ser)
button=Button(25, pull_up=True)
##########################################################################ROBOT#####################################################################################################
class Robot:
    def __init__(self):
        self.driving  = Motor(17, 18)
        self.steering = Motor(22, 23)
    i2c = busio.I2C(board.SCL, board.SDA)
    mpu = adafruit_mpu6050.MPU6050(i2c)
    def drive_forward(self, speed=0.5):
        self.driving.forward(speed=speed)
        
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
    #     return raw


    def stop(self):
        self.driving.stop()
        self.steering.stop()

    def move_forward(self, speed=1.0, distance_target=100):
        global Object
        Object = True
        global current_seen
        dist  = luna.get_distance()
        print("Starting move_forward â†’ target distance: " + str(dist) + " cm")
        start = time.time()
        while dist >= distance_target:
            self.drive_forward(speed)
            dist = luna.get_distance()
        self.stop()

    
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


        print("\nâœ“ All laps complete!")
    def luna_turn_left(self):
        global Object
        Object = False
        self.steering.backward(1.0)  # 
        time.sleep(0.8)  
        while timeout <= 10.0:
            self.driving.forward(0.8)
            timeout += 0.1  
            #print("gyro value z " + str(sensors6.mpu.gyro[1])+ " gyro value y " + str(sensors6.mpu.gyro[0]) + " gyro value x " + str(sensors6.mpu.gyro[2]))
            print(f"Turning... LiDAR distance: {luna.get_distance()} cm" + str(timeout) + " timer" )#
            time.sleep(0.01)  # small delay to avoid excessive polling
        self.keep_straight_left()  



    def move_in_lap_left(self, forward_speed=0.5, turn_speed=0.8,
                    distance_target=100, turn_angle=90, target_turns=12):
        global turns
        laps_completed = 0 
        print("object is not detected robot is moving")
        #turns = turn_counter
        while laps_completed <= 4:
            ######
            # self.drive_forward(speed=forward_speed)
            # self.wait(timeout=0.7)  # brief pause after turn
            print("turn 1 complete")
            
            self.move_forward(speed=forward_speed, distance_target=distance_target)
            self.luna_turn_left()
            # self.drive_forward(speed=forward_speed)
            # self.wait(timeout=1)  # brief pause after turn
            print("turn 2 complete")
            
            self.move_forward(speed=forward_speed, distance_target=distance_target)
            self.luna_turn_left()
            # self.drive_forward(speed=forward_speed)
            # self.wait(timeout=0.7)  # brief pause after turn
            print("turn 3 complete")
            
            self.move_forward(speed=forward_speed, distance_target=distance_target)
            self.luna_turn_left()
            # self.drive_forward(speed=forward_speed)
            # self.wait(timeout=0.7)  # brief pause after turn
            print("turn 4 complete")
            #turns = turn_counter
            #print( " turn " + str(turns) + " complete")
            laps_completed += 1
        print("\nâœ“ All laps complete!")


######

# ENTRY POINT
def button_code():
    print("code is starting and button has pressed")
    global turns
    
   
    t2 = threading.Thread(target=robot.move_in_lap_left({
            "forward_speed": 0.5,
            "turn_speed": 1.0,
            "distance_target": 60,
            "turn_angle": 1,
            "laps": 3
        }))
   
    t2.start()
    
    print("Obstacle detected! Stopping move_lap.")

def coin_flip():
    dist = luna.get_distance()
    robot.camera_turn_left(speed=0.5)
    if dist < 64:
        print("robot continues turning left")  
        robot.camera_turn_left(speed=0.5)
        robot.move_backwardin_lap_left(forward_speed=0.5, turn_speed=0.8,
                    distance_target=100, turn_angle=90, target_turns=12)
    elif dist > 64:
        print("robot continues turning right")
        robot.camera_turn_right(speed=0.5)
        robot.move_in_lap(forward_speed=0.5, turn_speed=0.8,
                    distance_target=100, turn_angle=90, laps=3)
###########################################################################MAIN######################################################################################################
if __name__ == "__main__":
    #calibrate_gyro_bias(samples=300, delay=0.01)
    robot = Robot()
    print("code is starting up...")
    distance = luna.get_distance()
    print(str(distance) + " cm")
    button.when_pressed=button_code
