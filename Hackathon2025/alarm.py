import time
import threading 

class Alarm:
#txt = string labelling the alarm
#timemax = time of the alarm in seconds, default at 5mins
#countdown = downcounter of the timer
#active = if the alarm is set and counting
#triggered = if the alarm is currently going off
    def __init__(self):
        self.txt = "Alarm"
        self.timemax = 300
        self.countdown = 300
        self.active = False
        self.triggered = False

    def set_txt(self, new_txt):
        self.text = new_txt

    def set_time(self, new_time):
        self.time = new_time

    def set_active(self, new_active):
        self.active = new_active

    def set_triggered(self, new_stat):
        self.triggered = new_stat