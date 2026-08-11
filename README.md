# RoboLords 2026 Future Engineers

## Abstract

We’re Team RoboLords from Maiden Erlegh School, competing in WRO 2026 Future Engineers. This repo tells the story of how our robot grew from rough LEGO SPIKE builds into a Raspberry Pi–powered RC truck that can handle both the Open Challenge and the Obstacle Challenge.

Our final robot uses:

- A Raspberry Pi 4B as the “brain”.
- Two TF-Luna LiDAR sensors for distance.
- A Raspberry Pi Camera Module 3 Wide for colour detection.
- A modified RC truck chassis with steering and drive controlled through a motor controller.

Over the season we discovered something important: a robot that finishes cleanly every time is worth more than one that’s only fast when everything goes perfectly. Most of our design decisions are about making it reliable, understandable, and reproducible under competition pressure.

## Team members

We’re Year 10 students at Maiden Erlegh School:

- **Parth Srivastav**
- **Raphael Peduru**

This project builds on our past WRO experience and a lot of hours spent testing, fixing, rebuilding, and improving the robot.

## Repository contents

We’ve tried to organise the repo so that someone who isn’t on our team can understand how the robot works:

- `README.md` – This main overview of the robot, hardware, software, and key decisions.
- `Engineering Journal.md` – Our journey: what we tried, what broke, and what we changed.
- `old code' is the code that we used to use like in the uk finals and now are useless as we switched to a more advanced code
- `schemes/` – Wiring diagrams and Raspberry Pi GPIO pin mapping.(https://github.com/ParthKSrivastav/RoboLords_2026_FE_Github/tree/main/schemes)
- `vehicle photos/` – Photos of the robot from front, rear, side, and top.(https://github.com/ParthKSrivastav/RoboLords_2026_FE_Github/tree/main/vehicle%20photos
- `team photo/` – Photo of the team with the robot.(https://github.com/ParthKSrivastav/RoboLords_2026_FE_Github/tree/main/team%20photo)

***

## 1. Mobility and mechanical design

### How the chassis evolved

We started where we were comfortable: LEGO SPIKE. Our first idea was to use two SPIKE hubs to split the work, but in practice the delay between them was too high for a car that has to react quickly to changing obstacles. Even when we dropped to a single hub, we kept hitting problems:

- The LEGO body was either too heavy, too fragile, or too flexible.
- Steering parts wore out or broke faster than we expected.
- The gyro in that setup wasn’t accurate enough to trust for three clean laps.

At that point, we realised we were spending more time fighting the platform than solving the challenge. So we moved to a pre-built RC vehicle. We tried several RC cars, but most were simply too small to fit a Raspberry Pi, motor controller, batteries, and wiring.

Eventually we found an RC truck that ticked the right boxes:

- A **load bed** at the back that acted like a proper storage bay.
- A working **Ackermann-style steering** system.
- Enough space inside to mount the electronics neatly.

This truck became the base for later versions of our robot.

### Steering, size and speed

The first truck body we used was big. It let us fit everything, but the size made tight turns harder and parking more awkward. As we started thinking more seriously about the Obstacle Challenge and parallel parking, this became a real limitation.

So we shrank the body in a later version:

- The new body is about 5 cm shorter.
- It still keeps the Ackermann steering and strong drive motor.

The side-effect of reducing size was that the robot suddenly felt **too fast**. With less weight and the same strong motor, it accelerated quickly and overshot turns. We solved this the simple way: we lowered the drive speed to 0.2 (20%). That single change made our turning and stopping much more predictable.

Inside the truck, we used LEGO blocks to separate the Pi, power bank, and motor controller. It’s not glamorous, but it keeps things from sliding around and made repairs in testing sessions a lot less stressful.

We also had a rule-related scare at one point. A truck with too many axles looked good but didn’t match the rules, so we had to swap it out. That reminded us that in Future Engineers, **following the rules** is just as important as technical performance.

***

## 2. Power and sensor architecture

### The brain and power

The robot’s brain is a **Raspberry Pi 4B**. We picked it because:

- It can handle camera processing and LiDAR at the same time.
- It has enough GPIO pins for motor control and extra sensors.
- There’s a lot of documentation and community support if we get stuck.

We power the Pi from a power bank, and the motor controller from a separate 9 V battery. Keeping those two supplies separate helps avoid brownouts when the motors draw more current. The Pi and motor controller share a common ground so the control signals are understood correctly.

### Sensors we ended up with

We experimented with quite a few sensors over the season. The final set is:

- **Front TF-Luna LiDAR** – Measures distance ahead and helps to avoid walls.
- **Rear TF-Luna LiDAR** – Added later for better awareness when parking.
- **Raspberry Pi Camera Module 3 Wide** – Detects red and green pillars in Round 2.

Along the way we tried:

- An **MPU6050 gyro** in the centre of the robot.
- Side **ultrasonic sensors**.

The gyro looked promising, and we tried Kalman filters and PID tuning, but in real runs it kept drifting and gave inconsistent angles. The ultrasonic sensors suffered from loose resistors and unreliable readings, especially when transported and plugged in repeatedly. In the end both were removed from the final design. That was one of the big lessons: if a sensor can’t be trusted in competition conditions, it’s better to remove it than to keep fighting it.

### Where we put everything

Sensor placement ended up being just as important as sensor choice:

- The **front TF-Luna** is low in the front bumper area, with LEGO pieces acting as a protective bumper so the sensor isn’t the first point of impact.
- The **rear TF-Luna** is low at the rear bumper so it can see the parking area behind the car.
- The **camera** started lower down near the windshield/hood for aesthetics, but the view was too limited. Moving it onto the roof gave us a much better field of view and more reliable colour detection.

The gyro, when we used it, was mounted close to the centre of the robot to reduce the effect of bumps. Even with that, it still wasn’t reliable enough, which is why it’s not part of the final setup.

### Wiring and GPIO map

Our GPIO table maps every Raspberry Pi pin to its job (LiDAR, motor controller, etc.). In our robot:

- **GPIO 17, 18, 22, 23** drive the motor controller inputs (IN1–IN4).
- TF-Luna uses UART and I2C for front and rear readings.
- The camera uses the Pi’s **ribbon cable camera port**, not GPIO pins, so high-speed video stays separate from sensor lines.

The motor controller wiring diagram shows:

- Motor live and ground going into the controller.
- The controller’s power coming from its own battery.
- A shared ground between the Pi and controller for correct signal levels.

Getting this right stopped a lot of the strange behaviour we saw in early tests.

***

## 3. Software architecture and obstacle strategy

### How the code is organised

The software started life as “one big file that does everything”. That was okay for early experiments, but it quickly became hard to read and debug.

We tried a three-file split (main / sensors / motor), but that introduced some import complexity at the worst time: right before events.

The final structure is deliberately simple:

- `round1.py` – Open Challenge behaviour (three laps).
- `round2.py` – Obstacle Challenge behaviour (red/green pillars + parking).
- `sensors6.py` – Shared sensor classes and helper functions for LiDAR.

This way, if someone wants to understand the Open Challenge, they read `round1.py` and `sensors6.py`. If they want Obstacle Challenge and parking, they read `round2.py` and `sensors6.py`.

### Round 1 – Open Challenge logic

Open Challenge starts by importing sensor support from `sensors6.py`. The core of the program is the `Robot` class, which contains:

- `drive_forward`, `move_forward`, `turn_left`, `turn_right`, `stop` and steering-correction functions.
- `luna_turn`, our turning system, which uses timed movement plus LiDAR checking to make turns more consistent.

On top of that, there’s a lap routine:

- Move forward a set distance.
- Turn 90 degrees using `luna_turn`.
- Repeat this four times for one lap.
- Repeat laps until three are completed.

We also use a basic **“coin flip”** idea that turns the robot and checks for walls. If it sees a wall, it chooses the other direction. If it doesn’t, it carries on. This is a simple way to adapt to track layout without hardcoding positions.

One of the biggest improvements came from reducing speed. At high speed we finished a run much faster, but the robot was inconsistent and hard to reproduce. Slowing down and accepting a slightly longer run gave us much cleaner three-lap behaviour.

### Round 2 – Obstacle Challenge logic

Round 2 builds on the same movement logic and adds a camera thread:

- The camera is configured with Picamera2.
- Frames are converted from RGB to HSV.
- Two red ranges and one green range are defined.
- Masks are created, cleaned with morphology, and contours found.
- When a valid contour is found, the code draws a rectangle and writes `RED` or `GREEN` on the frame.
- The current colour seen is stored in a shared variable `current_seen`.

While the camera is running, obstacle logic checks `current_seen`:

- If it’s green, the robot follows a sequence of 45° turns and straight segments to pass the pillar on the correct side.
- If it’s red, it uses a mirrored sequence on the other side.

We chose this approach because it is:

- Lightweight compared to full object detection.
- Easier to debug and tune.
- Good enough for reliably spotting the red/green pillars we care about.

### Parking behaviour

Parking logic comes in once the three laps are done and the robot is near the parking section. With the rear TF-Luna online, the robot now has a sense of how much space is behind it.

The idea is simple:

- Use short forward and backward moves.
- Use rear distance readings to avoid hitting the parking boundaries.
- Stop when the car is inside the parking area.

We added parking after we were confident the robot could complete laps and handle obstacles. This prevented us from having too many moving parts to debug at once.

***

## 4. Systems thinking and engineering decisions

A lot of our progress came from choosing what *not* to keep.

Some key decisions:

- Dropping **two-hub SPIKE** because of communication delay and complexity.
- Leaving **LEGO-only chassis** when we realised they couldn’t give the steering accuracy and durability we needed.
- Moving to an **RC truck** with a better steering system and more room for electronics.
- Removing **ultrasonic sensors** when resistor connections kept failing.
- Removing the **gyro** from the final design after repeated drift and instability.
- Raising the **camera** from the hood to the roof for a better view.
- Cutting **speed** down to 0.2 to improve accuracy and repeatability.

All of these were made after actual tests. In almost every case, the simpler solution was more reliable under competition conditions than the more complex one.

***

## 5. Reproducibility and GitHub quality

We want this repo to be useful to other teams and understandable for judges. That’s why it includes:

- Code for both rounds (`round1.py`, `round2.py`) plus shared sensor logic (`sensors6.py`).
- Wiring diagrams and GPIO tables.
- Photos of the robot from every side and top/down.
- A team photo.
- An Engineering Journal describing how the robot evolved over time.

### How to run the code (high level)

On the robot:

- Use `round1.py` when testing or running the **Open Challenge**.
- Use `round2.py` when testing or running the **Obstacle Challenge**.
- `sensors6.py` must be present because both rounds import LiDAR logic from it.

The robot follows the required competition start procedure:

1. Place the robot in the start zone, fully off.
2. Switch power on.
3. Wait in a ready state.
4. Press the start button when the judge says “Go”.

The GPIO wiring and sensor setup in this repo match that behaviour.

***

## Conclusion

Our Future Engineers robot didn’t come from a single perfect design. It came from:

- Breaking LEGO robots.
- Swapping out bodies and sensors.
- Watching the robot fail in competition.
- Then simplifying and tightening the design until it behaved predictably.

The biggest thing we learned is that in this category, the “best” robot isn’t the one with the most sensors or the craziest speed, it’s the one that **finishes reliably** and whose engineering can be explained clearly. That idea guided our choices in mechanics, wiring, sensors, and code, and it’s what this README is trying to share.
