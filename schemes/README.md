Motor controller wiring

Our motor_controller wiring diagram is a simple overview of how we power and control the drive motor on the robot.

In our setup:

    The motor’s live and ground wires go into the live and ground terminals on the motor controller.
    This means the controller can turn the motor on when we need it to move and cut the power when we want it to stop.

    The motor controller is powered by a 9 V battery, with its own live and ground going into the controller’s 5 V input.
    Keeping the motor power separate from the Raspberry Pi’s power helps avoid voltage drops on the Pi when the motor draws current.

    The controller and the Raspberry Pi share a common ground.
    This shared ground is important so the Pi’s control signals are understood correctly by the motor controller.

    The actual “drive” commands come from four GPIO pins on the Raspberry Pi (going to IN1, IN2, IN3, IN4 on the controller).
    In our build, we use GPIO 17, 18, 22 and 23. By switching these pins high or low in our code, the Pi tells the controller:

        when to turn the motors on or off,

        which way to drive,

        and when to stop.

Raspberry Pi GPIO wiring(you need to download the docx to see it, the FILE IS NOT EMPTY)

The Raspberry Pi GPIO pins diagram shows the full wiring layout for the robot. It makes it easy to see:

    Which GPIO pin is connected to each sensor or motor.

    What each pin does, using a description column (for example:
    “front TF-Luna LiDAR RX”, “rear TF-Luna TX”, “motor controller IN1”, “start button”, etc.).

Each GPIO pin is assigned to just one job. Because of that:

    It is really important that every wire ends up on the correct pin.
    Getting a pin wrong can:

        cause a sensor to stop working,

        make data inaccurate,

        or in the worst case, damage a component.

For the camera, we don’t use GPIO pins at all:

    The Raspberry Pi Camera Module 3 Wide is connected using the Pi’s FPC ribbon cable straight into the camera port.
    This keeps the camera on its dedicated high‑speed interface, and leaves the GPIO pins free for LiDAR, buttons, the motor controller, and any other sensors
