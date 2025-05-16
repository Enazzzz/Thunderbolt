# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       Zanea                                                        #
# 	Created:      1/1/2025, 10:49:14 PM                                        #
#                                                                              #
# ---------------------------------------------------------------------------- #

#! Library imports - Cannot import anything but Vex
from vex import *  # Import all necessary classes and functions from the Vex library for robot control.

#! Brain should be defined by default
brain = Brain()  # Instantiate the Brain object, which acts as the central processing unit for the robot.

# Initialize global variables for robot control and state tracking
press = 0  # Counter for button presses to select different autonomous routines.
f = FORWARD  # Shorthand for the FORWARD direction to simplify code readability.
r = REVERSE  # Shorthand for the REVERSE direction to simplify code readability.
d = DEGREES  # Shorthand for the DEGREES unit to simplify code readability.
p = PERCENT  # Shorthand for the PERCENT unit to simplify code readability.
forwards = False  # Flag to track forward movement, used for logic control.
turn_amt = 0  # Variable to store the amount of turn, used for precise movement control.
drive_percent = 38  # Initial drive speed percentage, adjustable for fine-tuning robot speed.
gyro_turn = 0  # Variable for gyro-based turning, though not used due to gyro issues.
est_balls_scored = 0  # Counter for estimated balls scored, used for performance tracking.

#* Sensor setup for object detection and navigation
# Back distance sensor for detecting objects behind the robot
back_distance = Distance(Ports.PORT9)  # Initialize a distance sensor on port 9 for rear object detection.

# Ball sensor for detecting balls on the field
ball_sensor = Distance(Ports.PORT4)  # Initialize a distance sensor on port 4 for ball detection.

# Gyro sensor for orientation tracking (not preferred due to inaccuracy)
gyro = Gyro(Ports.PORT10)  # Initialize a gyro sensor on port 10 for orientation tracking.

# Distcance sensor for detecting ball color and position
shooter_sensor = Distance(Ports.PORT8)  # Initialize a distance sensor on port 8 for ball color detection.

#* Motor setup for ball handling and movement
# Bottom accumulator for initial ball collection and transfer
bottom_acc = Motor(Ports.PORT12)  # Initialize a motor on port 12 for the bottom accumulator.
bottom_acc.set_stopping(HOLD)  # Configure the motor to hold its position when stopped to prevent ball rollback.
bottom_acc.set_max_torque(100, PERCENT)  # Set maximum torque to ensure reliable ball movement.
bottom_acc.set_velocity(100, PERCENT)  # Set velocity for efficient ball collection.
bottom_acc.reset_position()  # Reset the motor's position for accurate control.

# Top accumulator for assisting in ball movement
top_acc = Motor(Ports.PORT2)  # Initialize a motor on port 2 for the top accumulator.
top_acc.set_stopping(HOLD)  # Configure the motor to hold its position when stopped to prevent unintended movement.
top_acc.set_max_torque(100, PERCENT)  # Set maximum torque for reliable ball movement.
top_acc.set_velocity(100, PERCENT)  # Set velocity for efficient ball collection.
top_acc.reset_position()  # Reset the motor's position for accurate control.

# Mini accumulator for final ball handling before shooting
mini_acc = Motor(Ports.PORT11)  # Initialize a motor on port 11 for the mini accumulator.
mini_acc.set_max_torque(100, PERCENT)  # Set maximum torque for reliable ball movement.
mini_acc.set_velocity(100, PERCENT)  # Set velocity for efficient ball handling.
mini_acc.reset_position()  # Reset the motor's position for accurate control.
mini_acc.set_stopping(HOLD)  # Configure the motor to hold its position to maintain ball position before shooting.

#* Drivetrain motors for robot movement
# Left and right drive motors for main movement control
left_drive = Motor(Ports.PORT6)  # Initialize a motor on port 6 for the left drive.
right_drive = Motor(Ports.PORT1)  # Initialize a motor on port 1 for the right drive.
left_drive.set_max_torque(100, PERCENT)  # Set maximum torque for strong and reliable movement.
right_drive.set_max_torque(100, PERCENT)  # Set maximum torque for strong and reliable movement.
left_drive.set_velocity(100, PERCENT)  # Set velocity for fast movement.
right_drive.set_velocity(100, PERCENT)  # Set velocity for fast movement.

#* Shooting mechanism for scoring
shooter = Motor(Ports.PORT7)  # Initialize a motor on port 7 for the shooter.
shooter.set_velocity(100, PERCENT)  # Set velocity for maximum shooting power.
shooter.set_max_torque(100, PERCENT)  # Set maximum torque for reliable shooting.
shooter.set_stopping(HOLD)  # Configure the motor to hold its position to prevent gravity-induced movement.
shooter.reset_position()  # Reset the motor's position for accurate control.

#* Status indicator lights for visual feedback
# Right status light for indicating robot readiness
rbutton = Touchled(Ports.PORT3)  # Initialize a touch LED on port 3 for the right button.
rbutton.set_fade(FadeType.OFF)  # Disable fading to maintain a constant color.
rbutton.on(Color.RED)  # Set the LED color to red to indicate the robot is not ready.

# Left status light for indicating robot readiness
lbutton = Touchled(Ports.PORT5)  # Initialize a touch LED on port 5 for the left button.
lbutton.set_fade(FadeType.OFF)  # Disable fading to maintain a constant color.
lbutton.on(Color.RED)  # Set the LED color to red to indicate the robot is not ready.

def braincheck():
    """Increment the press counter and print its value for debugging."""
    global press  # Access the global press variable to modify it.
    press += 1  # Increment the press counter to track button presses.
    print(press)  # Output the current value of press for debugging purposes.

def change_percent():
    """Increase the drive speed percentage for fine-tuning robot speed."""
    global drive_percent  # Access the global drive_percent variable to modify it.
    drive_percent += 2  # Increment the drive speed percentage by 2 for speed adjustment.

def auto_1():
    """Execute the primary autonomous routine for competition strategy."""
    brain.timer.reset()  # Reset the timer to track the duration of the autonomous routine for optimization.
    global est_balls_scored  # Use the global variable to keep track of the number of balls scored.
    
    # Visual indicator that autonomous is running
    lbutton.set_color(Color.YELLOW)  # Set the left button LED to yellow to indicate the routine is active.
    rbutton.set_color(Color.YELLOW)  # Set the right button LED to yellow to indicate the routine is active.

    # Set drive motors to hold position during movements
    left_drive.set_stopping(HOLD)  # Ensure the left drive motor holds its position to prevent drift.
    right_drive.set_stopping(HOLD)  # Ensure the right drive motor holds its position to prevent drift.
    
    left_drive.set_velocity(35, p)  # Set the left drive motor to a slower speed for precise control.
    
    # Initial movement to position the robot for ball collection
    left_drive.spin_for(r, 250, d, False)  # Move the left drive motor in reverse to position the robot.
    right_drive.spin_for(f, 250, d, True)  # Move the right drive motor forward to position the robot.
    
    # Start collecting balls using the accumulators
    top_acc.spin(r, 100, p)  # Start the top accumulator to begin collecting balls.
    bottom_acc.spin(f, 100, p)  # Start the bottom accumulator to begin collecting balls.
    
    # Use the ball sensor to detect when a ball is within range
    while ball_sensor.object_distance() > 30:  # Continue until a ball is detected within 30 units.
        sleep(50)  # Pause briefly to allow for sensor reading.
        left_drive.spin(f, 35, p)  # Adjust the left drive motor to move forward slowly.
        right_drive.spin(r, 100, p)  # Adjust the right drive motor to move in reverse quickly.
        
    # Stop accumulators and drive motors once the ball is collected
    top_acc.stop()  # Stop the top accumulator once the ball is collected.
    bottom_acc.stop()  # Stop the bottom accumulator once the ball is collected.
    left_drive.stop()  # Stop the left drive motor to halt movement.
    right_drive.stop()  # Stop the right drive motor to halt movement.
    
    brain.timer.reset()
    # Move the robot back until it is close to the back wall
    while back_distance.object_distance() > 50 and brain.timer.time() <= 4000:  # Continue until the robot is within 10 units of the back wall.
        left_drive.spin(r, drive_percent, p)  # Adjust the left drive motor to move in reverse.
        right_drive.spin(f, 100, p)  # Adjust the right drive motor to move forward.
        sleep(50)  # Pause briefly to allow for sensor reading.
    
    left_drive.stop()  # Stop the left drive motor to halt movement.
    right_drive.stop()  # Stop the right drive motor to halt movement.
    
    sleep(250)  # Pause briefly to stabilize the robot's position.
    
    # Prepare to shoot the collected balls
    shooter.spin_for(r, 200, DEGREES, True)  # Prepare the shooter by spinning it in reverse.
    mini_acc.spin(f, 100, p)  # Start the mini accumulator to position the ball for shooting.
    top_acc.spin(r, 100, p)  # Start the top accumulator to position the ball for shooting.
    bottom_acc.spin(f, 100, p)  # Start the bottom accumulator to position the ball for shooting.
    shooter.spin_for(f, 750, DEGREES, True)  # Shoot the ball by spinning the shooter forward.
    
    # Ensure the ball is correctly positioned before shooting
    while shooter_sensor.object_distance() >= 10:
        sleep(50)  # Pause briefly to allow for sensor reading.
    
    sleep(300)  # Pause briefly to ensure the ball is shot.
    
    # Stop all accumulators after shooting
    mini_acc.stop()  # Stop the mini accumulator after shooting.
    top_acc.stop()  # Stop the top accumulator after shooting.
    bottom_acc.stop()  # Stop the bottom accumulator after shooting.

    est_balls_scored += 2  # Update the estimated number of balls scored.
    print("Time: {}  Balls Scored: {}".format(brain.timer.time(), est_balls_scored))  # Output the time and balls scored for feedback.
    
    # Reset the shooter for the next round
    shooter.spin_for(REVERSE, 2350, DEGREES, False)  # Reset the shooter position for the next round.
    
    # Reposition the robot for the next phase
    left_drive.spin_for(f, 100, d, False)  # Move the left drive motor forward to reposition the robot.
    right_drive.spin_for(r, 100, d, True)  # Move the right drive motor in reverse to reposition the robot.
    
    # End of autonomous routine
    lbutton.set_color(Color.GREEN)  # Set the left button LED to green to indicate the routine is complete.
    rbutton.set_color(Color.GREEN)  # Set the right button LED to green to indicate the routine is complete.
    left_drive.set_stopping(COAST)  # Allow the left drive motor to coast after stopping.
    right_drive.set_stopping(COAST)  # Allow the right drive motor to coast after stopping.
    left_drive.stop()  # Stop the left drive motor.
    right_drive.stop()  # Stop the right drive motor.

def auto_2():
    """Execute the secondary autonomous routine, typically after repositioning the robot."""
    # Visual indicator that autonomous is running
    lbutton.set_color(Color.YELLOW)  # Set the left button LED to yellow to indicate the routine is active.
    rbutton.set_color(Color.YELLOW)  # Set the right button LED to yellow to indicate the routine is active.
    global est_balls_scored  # Use the global variable to keep track of the number of balls scored.
    
    # Set drive motors to hold position during movements
    left_drive.set_stopping(HOLD)  # Ensure the left drive motor holds its position to prevent drift.
    right_drive.set_stopping(HOLD)  # Ensure the right drive motor holds its position to prevent drift.

    
    # Initial movement to position the robot for ball collection
    left_drive.spin_for(r, 300, d, False)  # Move the left drive motor in reverse to position the robot.
    right_drive.spin_for(f, 300, d, True)  # Move the right drive motor forward to position the robot.
    
    # Start collecting balls using the accumulators
    top_acc.spin(r, 100, p)  # Start the top accumulator to begin collecting balls.
    bottom_acc.spin(f, 100, p)  # Start the bottom accumulator to begin collecting balls.
    
    # Move the robot to align with the ball
    left_drive.spin_for(f, 150, d, False)  # Move the left drive motor forward to align with the ball.
    right_drive.spin_for(r, 150, d, True)  # Move the right drive motor in reverse to align with the ball.
    
    # Use the ball sensor to detect when a ball is within range
    while ball_sensor.object_distance() < 30:  # Continue until a ball is detected closer than 30 units.
        sleep(50)  # Pause briefly to allow for sensor reading.
        
    sleep(400)  # Pause briefly to stabilize the robot's position.
    
    # Use the ball sensor to detect when a ball is out of range
    while ball_sensor.object_distance() > 30:  # Continue until a ball is detected farther than 30 units.
        sleep(50)  # Pause briefly to allow for sensor reading.
        left_drive.spin(f, 100, p)  # Adjust the left drive motor to move forward quickly.
        right_drive.spin(r, 100, p)  # Adjust the right drive motor to move in reverse quickly.
    
    # Stop accumulators and drive motors once the ball is collected
    left_drive.stop()  # Stop the left drive motor to halt movement.
    right_drive.stop()  # Stop the right drive motor to halt movement.
    
    top_acc.stop()  # Stop the top accumulator once the ball is collected.
    bottom_acc.stop()  # Stop the bottom accumulator once the ball is collected.
    
    # Move the robot back to the starting position
    left_drive.spin(r, 100, p)  # Spin the left drive motor in reverse at full speed.
    right_drive.spin(f, 100, p)  # Spin the right drive motor forward at full speed.
    
    sleep(2000)  # Pause to allow the robot to reach the starting position.
    
    left_drive.stop()
    right_drive.stop()
    
    # Use the back distance sensor to align with the wall
    while back_distance.object_distance() > 50 and brain.timer.time() <= 4000: # Continue until the robot is within 50 units of the back wall.
        left_drive.spin(r, 50, p)  # Adjust the left drive motor to move in reverse slowly.
        right_drive.spin(f, 50, p)  # Adjust the right drive motor to move forward slowly.
        sleep(50)  # Pause briefly to allow for sensor reading.
    
    left_drive.stop()  # Stop the left drive motor to halt movement.
    right_drive.stop()  # Stop the right drive motor to halt movement.
    
    sleep(500)  # Pause briefly to stabilize the robot's position.
    
    # Prepare to shoot the collected balls
    shooter.spin_for(r, 200, DEGREES, True)  # Prepare the shooter by spinning it in reverse.
    shooter.spin_for(f, 750, DEGREES, True)  # Shoot the ball by spinning the shooter forward.
    
    mini_acc.spin(f, 100, p)  # Start the mini accumulator to position the ball for shooting.
    top_acc.spin(r, 100, p)  # Start the top accumulator to position the ball for shooting.
    bottom_acc.spin(f, 100, p)  # Start the bottom accumulator to position the ball for shooting.
    
    # Ensure the ball is correctly positioned before shooting
    while shooter_sensor.object_distance() >= 10:
        sleep(50)  # Pause briefly to allow for sensor reading.
        
    sleep(2000)  # Pause briefly to ensure the ball is shot.
    
    mini_acc.stop()  # Stop the mini accumulator after shooting.
    
    est_balls_scored += 2  # Update the estimated number of balls scored.
    print("Time: {}  Balls Scored: {}".format(brain.timer.time(), est_balls_scored))  # Output the time and balls scored for feedback.
    
    # Repeat the process to collect and shoot more balls
    for _ in range(6):  # Repeat the following block 6 times
        right_drive.set_velocity(75,p)
        left_drive.set_velocity(100,p)
        left_drive.spin_for(f, 850, d, False)  # Move the left drive motor forward to reposition the robot.
        right_drive.spin_for(r, 850, d, True)  # Move the right drive motor in reverse to reposition the robot.

        left_drive.spin(r, 75, p)  # Spin the left drive motor in reverse at full speed.
        right_drive.spin(f, 75, p)  # Spin the right drive motor forward at full speed.

        sleep(3000)  # Pause to allow the robot to reach the starting position.

        left_drive.stop()  # Stop the left drive motor to halt movement.
        right_drive.stop()  # Stop the right drive motor to halt movement.

        # Use the back distance sensor to align with the wall
        while back_distance.object_distance() > 50 and brain.timer.time() <= 4000:  # Continue until the robot is within 50 units of the back wall.
            left_drive.spin(r, 100, p)  # Adjust the left drive motor to move in reverse at full speed.
            right_drive.spin(f, 100, p)  # Adjust the right drive motor to move forward at full speed.
            sleep(50)  # Pause briefly to allow for sensor reading.
        
        mini_acc.spin(f, 100, p)  # Start the mini accumulator to position the ball for shooting.
        top_acc.spin(r, 100, p)  # Start the top accumulator to position the ball for shooting.
        bottom_acc.spin(f, 100, p)  # Start the bottom accumulator to position the ball for shooting.
        
        # Ensure the ball is correctly positioned before shooting
        while shooter_sensor.object_distance() >= 10:
            sleep(50)  # Pause briefly to allow for sensor reading.
        sleep(500)  # Pause briefly to ensure the ball is shot.
        while shooter_sensor.object_distance() >= 10:
            sleep(50)  # Pause briefly to allow for sensor reading.
        sleep(500)  # Pause briefly to ensure the ball is shot.
        mini_acc.stop()  # Stop the mini accumulator after shooting.
        est_balls_scored += 2  # Update the estimated number of balls scored.
        print("Time: {}  Balls Scored: {}".format(brain.timer.time(), est_balls_scored))  # Output the time and balls scored for feedback.

def button():
    """Handle button presses to select and execute autonomous programs."""
    global press  # Access the global press variable to modify it.
    press += 1  # Increment the press counter to cycle through autonomous programs.
    if press == 1:  # If press counter is 1
        auto_1()  # Execute the auto_1 function
    elif press == 2:  # If press counter is 2
        auto_2()  # Execute the auto_2 function
    elif press != range(0, 2):  # If press counter is not in the range 0-2
        press = 0  # Reset the press counter to 0

def reset():
    """Reset the shooter position to its initial state."""
    shooter.spin_for(REVERSE, 2350, DEGREES, False)  # Spin shooter in reverse for 2350 degrees to reset position.

# Assign functions to button press events for user interaction
lbutton.pressed(button)  # Assign the button function to the left button press event
rbutton.pressed(button)  # Assign the button function to the right button press event
brain.buttonCheck.pressed(braincheck)  # Assign the braincheck function to the brain button check event
brain.buttonLeft.pressed(reset)  # Assign the reset function to the left brain button press event
brain.buttonRight.pressed(change_percent)  # Assign the change_percent function to the right brain button press event