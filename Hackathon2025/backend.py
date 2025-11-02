import time
import RPi.GPIO as GPIO
import requests
from guizero import App, Box, Text, PushButton
from functools import partial

# --- Hardware Configuration ---
SERVO_PIN = 11
BUTTON_PIN = 7

# --- GPIO Setup ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Using internal pull-down
pwm = GPIO.PWM(SERVO_PIN, 50)

# --- Global Variables for Timer ---
timer_minutes = 0
timer_seconds = 0
total_seconds = 0

# --- Hardware Functions ---

def angle_to_duty(angle):
    """Converts a servo angle to a PWM duty cycle."""
    return 2 + (angle / 18)

def trigger_servo():
    """NON-BLOCKING: Moves the servo and starts checking for the hardware button."""
    print("ALARM: Timer finished. Moving servo to 30 degrees.")
    # Show the "alarm active" message on the GUI
    timer_display.value = "ALARM ACTIVE"
    status_text.value = "Press hardware button to stop."
    
    pwm.start(angle_to_duty(180))
    time.sleep(0.5)
    
    # CRITICAL: Instead of a blocking while loop, we schedule a function to check the button
    app.repeat(100, check_hardware_button) # Check for button press every 100ms

def stop_alarm():
    pwm.ChangeDutyCycle(angle_to_duty(0))
    time.sleep(0.5)

def cleanup():
    print("Cleaning up GPIO.")
    GPIO.cleanup()
    app.destroy()

# --- GUI Functions ---

def update_time_display():
    global timer_minutes, timer_seconds
    # Format to always have two digits (e.g., 05, 09, 10)
    minutes_text.value = f"{timer_minutes:02d}"
    seconds_text.value = f"{timer_seconds:02d}"

def adjust_time(unit, amount):
    global timer_minutes, timer_seconds
    if unit == "min":
        timer_minutes += amount
        if timer_minutes < 0: timer_minutes = 0
        if timer_minutes > 59: timer_minutes = 59
    elif unit == "sec":
        timer_seconds += amount
        if timer_seconds < 0: timer_seconds = 0
        if timer_seconds > 59: timer_seconds = 59
    update_time_display()

def start_countdown():
    global total_seconds
    total_seconds = (timer_minutes * 60) + timer_seconds
    if total_seconds > 0:
        show_countdown_display()
        update_countdown()
        # Schedule the countdown updater to run every 1000ms (1 second)
        app.repeat(1000, update_countdown)

def update_countdown():
    global total_seconds
    
    if total_seconds > 0:
        mins, secs = divmod(total_seconds, 60)
        timer_display.value = f"{mins:02d}:{secs:02d}"
        total_seconds -= 1
    else:
        # Timer has finished
        app.cancel(update_countdown) # Stop the countdown repeater
        trigger_servo() # Trigger the physical alarm

def check_hardware_button():
    if GPIO.input(BUTTON_PIN) == 1:
        app.cancel(check_hardware_button) # Stop checking the button
        stop_alarm()
        reset_gui()

def reset_gui():
    status_text.value = "Set the timer duration."
    show_timer_controls()

# --- GUI Layout and Widgets ---

def show_timer_controls():
    timer_controls_box.show()
    countdown_box.hide()

def show_countdown_display():
    timer_controls_box.hide()
    countdown_box.show()

app = App(title="Hardware Alarm Timer", width=400, height=250)
app.on_close(cleanup) # Make sure GPIO is cleaned up when window is closed

# -- Box for Timer Setup Controls --
timer_controls_box = Box(app, layout="grid")

# Minute controls
PushButton(timer_controls_box, text="+", command=partial(adjust_time, "min", 1), grid=[0,0])
minutes_text = Text(timer_controls_box, text="00", size=40, grid=[0,1])
PushButton(timer_controls_box, text="-", command=partial(adjust_time, "min", -1), grid=[0,2])

# Separator
Text(timer_controls_box, text=":", size=40, grid=[1,1])

# Second controls
PushButton(timer_controls_box, text="+", command=partial(adjust_time, "sec", 1), grid=[2,0])
seconds_text = Text(timer_controls_box, text="00", size=40, grid=[2,1])
PushButton(timer_controls_box, text="-", command=partial(adjust_time, "sec", -1), grid=[2,2])

# Start Button
start_button = PushButton(app, text="Start Timer", command=start_countdown)
start_button.text_size = 16

# -- Box for Countdown Display --
countdown_box = Box(app, visible=False)
timer_display = Text(countdown_box, text="", size=60)
status_text = Text(app, text="Set the timer duration.")

# --- Initial State ---
update_time_display()
app.display()

