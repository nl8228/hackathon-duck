import time
import RPi.GPIO as GPIO
import requests
from guizero import App, Box, Text, PushButton
from functools import partial

# --- Hardware Configuration ---
SERVO_PIN  = 11
BUTTON_PIN = 7
ALARM_PIN  = 37

# --- GPIO Setup ---
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(ALARM_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # internal pull-down
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz for typical servo
GPIO.output(ALARM_PIN, GPIO.LOW)

# --- Global timer state ---
timer_minutes = 0
timer_seconds = 0
total_seconds = 0
is_paused = False

# ---------------- Hardware helpers ----------------
def angle_to_duty(angle):
    """Convert a servo angle to a PWM duty cycle."""
    return 2 + (angle / 18)

def stop_alarm():
    """Return servo, stop beeper/LED, etc."""
    try:
        pwm.ChangeDutyCycle(angle_to_duty(90))
    except Exception:
        pass
    GPIO.output(ALARM_PIN, GPIO.LOW)
    time.sleep(0.5)

def cleanup():
    """Ensure GPIO is reset when app closes."""
    print("Cleaning up GPIO.")
    try:
        GPIO.cleanup()
    finally:
        # guizero handles window teardown
        pass

# ---------------- GUI callbacks ----------------
def update_time_display():
    """Refresh the 00:00 labels in the setup view."""
    minutes_text.value = f"{timer_minutes:02d}"
    seconds_text.value = f"{timer_seconds:02d}"

def adjust_time(unit, amount):
    """Increment/decrement minutes or seconds (0..59)."""
    global timer_minutes, timer_seconds
    if unit == "min":
        timer_minutes += amount
        if timer_minutes < 0:
            timer_minutes = 0
        if timer_minutes > 59:
            timer_minutes = 59
    elif unit == "sec":
        timer_seconds += amount
        if timer_seconds < 0:
            timer_seconds = 0
        if timer_seconds > 59:
            timer_seconds = 59
    update_time_display()

def show_timer_controls():
    """Show the setup controls; hide countdown view."""
    timer_controls_box.show()
    countdown_box.hide()
    countdown_controls_box.hide()
    status_text.value = "Set the timer duration."
    start_button.show()

def show_countdown_display():
    """Show the countdown and control buttons; hide setup controls."""
    timer_controls_box.hide()
    countdown_box.show()
    countdown_controls_box.show()
    status_text.value = "Timer Running"

def check_hardware_button():
    """If external button pressed, stop alarm and reset UI."""
    if GPIO.input(BUTTON_PIN) == 1:
        app.cancel(check_hardware_button)  # stop polling
        stop_alarm()
        reset_gui()

def trigger_servo():
    """Timer finished: move servo and start checking hardware button."""
    timer_display.value = "Ringing"
    # Hide pause control, show instruction to stop
    pause_resume_button.hide()
    status_text.value = "Close Duck Head to stop."
    GPIO.output(ALARM_PIN, GPIO.HIGH)
    pwm.start(angle_to_duty(0))
    time.sleep(0.5)
    # poll the hardware button until user presses it
    app.repeat(100, check_hardware_button)  # every 100 ms

def start_countdown():
    """Begin the countdown loop if duration > 0."""
    start_button.hide()
    global total_seconds, is_paused
    is_paused = False
    total_seconds = (timer_minutes * 60) + timer_seconds
    if total_seconds > 0:
        pause_resume_button.text = "Pause"
        pause_resume_button.show()
        show_countdown_display()
        update_countdown()
        app.repeat(1000, update_countdown)  # tick every second

def update_countdown():
    """Tick once per second while running; finish by triggering alarm."""
    global total_seconds
    if is_paused:
        return
    if total_seconds > 0:
        mins, secs = divmod(total_seconds, 60)
        timer_display.value = f"{mins:02d}:{secs:02d}"
        total_seconds -= 1
    else:
        # Countdown finished
        app.cancel(update_countdown)
        trigger_servo()

def toggle_pause():
    """Toggle paused state and update UI."""
    global is_paused
    is_paused = not is_paused
    if is_paused:
        pause_resume_button.text = "Resume"
        status_text.value = "Timer Paused"
    else:
        pause_resume_button.text = "Pause"
        status_text.value = "Timer Running"

def close_timer():
    """User closed timer; stop loops and reset."""
    try:
        app.cancel(update_countdown)
    except Exception:
        pass
    reset_gui()

def reset_gui():
    """Return to initial state and stop any alarm/pollers."""
    global is_paused
    is_paused = False
    try:
        app.cancel(check_hardware_button)
    except Exception:
        pass
    stop_alarm()
    show_timer_controls()

# ------------------- GUI layout -------------------
app = App(title="Timer", width=400, height=250)
app.when_closed = cleanup  # ensure GPIO cleanup on exit

# Box for timer setup controls (grid: columns 0..2, rows 0..2)
timer_controls_box = Box(app, layout="grid")

# Minute controls
PushButton(
    timer_controls_box, text="+",
    command=partial(adjust_time, "min", 1), grid=[0, 0]
)
minutes_text = Text(timer_controls_box, text="00", size=40, grid=[0, 1])
PushButton(
    timer_controls_box, text="-",
    command=partial(adjust_time, "min", -1), grid=[0, 2]
)

# Separator
Text(timer_controls_box, text=":", size=40, grid=[1, 1])

# Second controls
PushButton(
    timer_controls_box, text="+",
    command=partial(adjust_time, "sec", 1), grid=[2, 0]
)
seconds_text = Text(timer_controls_box, text="00", size=40, grid=[2, 1])
PushButton(
    timer_controls_box, text="-",
    command=partial(adjust_time, "sec", -1), grid=[2, 2]
)

# Start button
start_button = PushButton(app, text="Start Timer", command=start_countdown)
start_button.text_size = 16

# Pause / Resume / Close controls (hidden until running)
countdown_controls_box = Box(app, layout="grid", visible=False)
pause_resume_button = PushButton(
    countdown_controls_box, text="Pause",
    command=toggle_pause, grid=[0, 0]
)
close_timer_button = PushButton(
    countdown_controls_box, text="Close Timer",
    command=close_timer, grid=[1, 0]
)

# Countdown display (hidden until running)
countdown_box = Box(app, visible=False)
timer_display = Text(countdown_box, text="", size=60)

# Status message
status_text = Text(app, text="Set the timer duration.")

# Initial UI state
update_time_display()
show_timer_controls()

app.display()

