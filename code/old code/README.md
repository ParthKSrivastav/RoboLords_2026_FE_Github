Contains our code, round 1 being the open challenge, sensors6.py which contains all our sensor info, calibration and functions for the sensors, and round 2 being obstacle challenge.



Round 1 open challenge:

Our code starts begins by importing all sensor information for sensors6

then defines Robot class. Class in python is " like an object constructor, or a "blueprint" for creating objects " - GeeksforGeeks

&#x20;   -> robot class contains all the motor functions such as "drive\_forward" and "move\_forward"

then the code defines the "more complex" functions such as luna\_turn which is our 90degree turn system which combines time + gyro to give accurate turns

Then it defines the lap logic which is a simple loop with 4 move\_forward logics and 4 luna\_turns then print which lap it is on. 

Then we have the coin\_flip which turns the robot 45 degrees to scan for a wall, if there is no wall it continues that way otherwise turns and drives in the other direction.

We then come to the button code which contains the coin\_flip and in our round2 code it adds the camera logic using threading(this is the main difference between our round 1 and round 2 code)

Then we have the main which contains distance print statement for debugging and holds the code until the button is pressed and released.

Round 2 obstacle challenge:

Our code for round 2 is the same as round 1 just with a camera logic.

Camera logic (simply):

starts by configuring and enabling the camera

Sets values for green and red

Then for an infinite loop (While True)

It creates red and green masks using the hsv(Hue, Saturation, and Value)

it makes live camera feed and checks for red \& green

\-> if it detects the colours it prints a rectangle and labels it whichever colour it also puts the value into a                                    variable called "current\_seen" which is set to None at the beginning of the code. Then changed to either "red" or "green" depending on the colour

Then the function "colour\_detection" takes the values from "current\_seen" and completes the action required  

