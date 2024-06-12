from machine import Pin, PWM, Timer
import utime
from mqtt_client import MClient  # Import your MQTT client module here
from ina219 import INA219  # Import the INA219 class from your module

# Initialize MQTT client
client = MClient()

# Pin allocations for Analog inputs and other pins
va_pin = Pin(28, Pin.IN)
vb_pin = Pin(26, Pin.IN)
vpot_pin = Pin(27, Pin.IN)

# PWM setup
pwm = PWM(Pin(9))
pwm.freq(100000)
min_pwm = 20000
max_pwm = 55000
pwm_out = min_pwm

# Global variables for control and timers
global timer_elapsed
timer_elapsed = 0
count = 0
first_run = True

# Shunt resistance value
global SHUNT_OHMS
SHUNT_OHMS = 0.10

# Moving average filter class
class MovingAverageFilter:
    def __init__(self, size=5):
        self.size = size
        self.values = []

    def add_value(self, value):
        if len(self.values) >= self.size:
            self.values.pop(0)
        self.values.append(value)

    def get_average(self):
        return sum(self.values) / len(self.values) if self.values else 0

# Constants and variables for control
prev_va = 0
prev_iL = 0
current_duty = min_pwm
step = 500
hysteresis_band = 0.1
prev_power = 0

# Function to send power data via MQTT
def send_power_data(power):
    # Replace with actual MQTT publish function
    client.send_pv_power(power)

# Incremental Conductance MPPT function
def mppt_incremental_conductance():
    global timer_elapsed, count, first_run, prev_va, prev_iL, current_duty, step, prev_power

    # Initialize INA219 instance
    ina = INA219(SHUNT_OHMS, 64, 5)
    ina.configure()

    while True:
        if first_run:
            loop_timer = Timer(mode=Timer.PERIODIC, freq=500, callback=tick)
            first_run = False

        if timer_elapsed == 1:
            va = 1.017 * (12490 / 2490) * 3.3 * va_pin()  # Adjusted for Pin usage
            vb = 1.015 * (12490 / 2490) * 3.3 * vb_pin()  # Adjusted for Pin usage
            Vshunt = ina.vshunt()
            iL = Vshunt / SHUNT_OHMS

            va_filter.add_value(va)
            iL_filter.add_value(iL)
            va = va_filter.get_average()
            iL = iL_filter.get_average()

            delta_iL = iL - prev_iL
            delta_va = va - prev_va

            output_power = vb * iL
            output_power = round(output_power, 5)
            prev_power = round(prev_power, 5)

            if delta_va != 0:
                incremental_conductance = delta_iL / delta_va
                instantaneous_conductance = -iL / va

                incremental_conductance = round(incremental_conductance, 5)
                instantaneous_conductance = round(instantaneous_conductance, 5)

                if incremental_conductance == instantaneous_conductance:
                    pass
                elif incremental_conductance > instantaneous_conductance + hysteresis_band:
                    current_duty -= step
                elif incremental_conductance < instantaneous_conductance - hysteresis_band:
                    current_duty += step

                current_duty = saturate(current_duty, max_pwm, min_pwm)
                pwm.duty_u16(current_duty)

                send_power_data(output_power)

            prev_va = va
            prev_iL = iL
            prev_power = output_power

            utime.sleep_ms(10)

            count += 1
            timer_elapsed = 0

            if count > 30:
                print(f"Output Power: {output_power:.3f}")
                count = 0

# Timer callback function
def tick(t):
    global timer_elapsed
    timer_elapsed = 1

# Start MPPT algorithm
mppt_incremental_conductance()

