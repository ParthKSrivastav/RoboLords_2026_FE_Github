# RoboLords_2026_FE_Github
Meet Team Robolords

We’re Team Robolords from Maiden Erlegh School, and this repo documents our journey in WRO Future Engineers — from early experiments to the robot we’re taking to the UK finals.

Our team:

    Parth Srivastav – Has competed three times before in WRO RoboMission (Junior and Elementary). He’s into robotics, Raspberry Pi projects, sensors like LiDAR and gyros, and plays the piano.

    Raphael Peduru – Has previous experience in WRO Future Engineers. He enjoys robotics, acting, piano, and trying out new challenges, from sports to engineering.

    Jai Kumar Kairamakonda – Year 10 student and UK finals participant, helping develop and refine the robot for competition.

We’re all in Year 10, aged 14–15, and this project is the result of several years of learning, testing, and improving our designs.
What our robot does

Our robot is designed to:

    Drive autonomously around the WRO Future Engineers field.

    Complete accurate and repeatable laps for the Open Challenge.

    Detect and react to red and green markers in the Obstacle Challenge.

    Park reliably at the end of the run.

To do that, we combine:

    Electrical wiring and power distribution.

    Sensor integration (LiDAR, camera, gyro).

    Vehicle control software.

    Circuit design around a Raspberry Pi 4B.

    A modified RC truck chassis for realistic steering and storage.

We learned quickly that a robot that is consistent is more valuable than one that is just fast. Most of our design decisions are about making the robot reliable and reproducible under competition pressure.
Brain of the robot: Raspberry Pi 4B

At the centre of the system is a Raspberry Pi 4B (8 GB RAM). We chose it because:

    It’s powerful enough for computer vision and sensor fusion.

    It can talk to LiDAR, gyros, and the motor controller at the same time.

    It’s widely used in education, with good documentation and community support.

The Pi is powered by a 5000 mAh power bank, which gives us up to about 8 hours of operation, so we don’t have to worry about the robot dying in the middle of testing or a run.
Sensors and situational awareness
LiDAR (TF-Luna)

We use TF-Luna LiDAR sensors for distance measurement:

    Front TF-Luna – Stops frontal collisions and detects walls ahead.

    Rear TF-Luna – Added later to improve parking and awareness behind the robot.

TF-Luna works on the time-of-flight principle: it sends a light pulse, measures how long it takes to come back, and converts that into distance. We tuned it to send pulses at a high rate so the robot always has a fresh picture of what’s in front and behind.
Camera

We tested two camera options:

    DFRobot Huskylens – Attractive because of onboard image processing.

    Raspberry Pi Camera Module 3 Wide – Became our final choice.

Huskylens was powerful, but we had trouble integrating it cleanly with the Pi. The wide Pi camera gave us:

    A larger field of view (better awareness for Obstacle Challenge).

    A clean ribbon cable connection to the Pi.

    Flexibility to use OpenCV and our own colour-detection logic.

We briefly tried using Ultralytics for object detection, but installation issues and environment conflicts made it overkill for our needs. In the end we wrote our own colour detection code using OpenCV. It’s lighter, simpler, and accurate enough for detecting the red and green markers we need in Round 2.
Gyro

We originally used an MPU6050 gyro mounted near the centre of the robot, just behind the camera, to estimate orientation and help with precise turning.

However, in practice it kept giving us inconsistent readings. We tried:

    Kalman filters.

    PID controllers.

    Combinations of both.

Despite all that, the MPU6050 remained too unstable for reliable three-lap runs, so we eventually removed it from the final design and focused on methods that gave us more predictable behaviour.
Chassis and mechanical design

We started on LEGO SPIKE Prime, building on our earlier robotics work. While this was familiar, we ran into several problems:

    Building Ackermann steering with SPIKE parts was difficult.

    Steering connectors were fragile and broke often.

    The platform didn’t give us the robustness we needed.

To solve this, we switched to a remote-controlled truck as our base:

    We wired its motors to the Raspberry Pi through an L298N motor controller.

    The truck’s rear storage compartment became a neat space for the Pi, battery, and controller.

    The design looked more like a real vehicle and less like a prototype with wires everywhere.

We used LEGO blocks inside the truck to separate and secure each unit (Pi, power bank, motor controller), so they stayed in place and didn’t interfere with one another during runs.

At one point we used a truck with too many axles, which nearly got us disqualified because it didn’t match the rules. That forced us to change to a smaller mini-truck (our Mark 11/12 versions) and reminded us that rule compliance is as important as performance.
Sensor placement

Placement matters just as much as choice of sensor:

    Front TF-Luna is at the bottom of the driver’s cabin for a clear view ahead.

    Rear TF-Luna is placed to see behind the vehicle during parking.

    The Pi camera is mounted on top of the cabin to maximise field of view.

    The gyro (in earlier versions) was placed near the centre to reduce noise from uneven movement.

We tested and adjusted positions to reduce blind spots and vibrations. Even a good sensor behaves badly if it’s mounted poorly.
Software architecture

Our code went through several iterations.
Early approach

At first, everything lived in one big file. This worked for quick experiments, but:

    It became hard to read.

    Debugging was slow.

    Changing one part risked breaking another.

Three-file split

We then split into:

    A main file – high-level logic.

    A sensor file – all sensor code (camera, LiDAR, gyro).

    A motor file – movement functions and motor control.

This was better in theory, but we ran into import/module issues and it added complexity we didn’t really need.
Final structure

In the end, we simplified to:

    Motor logic file – Contains movement functions and the main lap/obstacle logic.

    Sensors file – Contains all sensor classes and functions (LiDAR, camera, gyro where used).

    Single main entry function – A high-level function that starts the three-lap behaviour.

The motor logic calls sensor functions (e.g., luna for LiDAR, camera colour detection, and gyro routines where applicable). This setup makes the code:

    Easier to debug.

    Easier to tune (speed, stopping distance, turning angles).

    Easier to understand for someone reading the repo.

How it behaves in each round
Round 1 – Open Challenge

Goal: clean, repeatable laps.

    The robot drives a set number of laps using distance and timing.

    Turn and movement functions are tuned for consistency instead of maximum speed.

    We discovered that a slower but accurate run often scores more points than a faster but unreliable one.

Round 2 – Obstacle Challenge

Goal: react correctly to red/green markers and complete laps.

    Camera logic runs in parallel with movement.

    Our colour detection code identifies red and green markers and stores the current seen colour.

    Movement logic then adjusts path so markers are passed on the correct side.

Parking

Goal: finish the run with a clean park.

    With the rear TF-Luna added, the robot gets better distance measurements behind it.

    Parking logic uses forward/back movements and distance readings to line up and stop in the parking bay.

    We tuned this after getting basic obstacle behaviour working, to avoid too many moving parts at once.

Lessons we learned

From building this robot and preparing for WRO, a few lessons stood out:

    More hardware doesn’t automatically mean a better robot.

    If a sensor or library is too hard to integrate reliably, it’s often better to switch to something simpler.

    How the robot looks matters, but performance and rule compliance matter more.

    Keeping code structure simple can save you in competition when time and nerves are tight.

    A robot that always finishes its run is more valuable than one that crashes trying to be fast.

    Having offline access (monitor, mouse, keyboard) and a safe start button can prevent last-minute disasters.
