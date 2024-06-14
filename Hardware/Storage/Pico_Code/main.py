from machine import Pin, PWM, Timer, ADC, I2C
import utime
from ina219 import INA219
from pid_controller import PIDController
from helper_functions import saturate, get_desired_power, calculate_soc, update_pid_gains
from mqtt_client import MClient, Device

# connect to wifi and broker
client = MClient(Device.STORAGE)

# Constants
SHUNT_OHMS = 0.1
C = 0.25
MAX_CAPACITY = 25.0

# Initialization
va_pin = ADC(Pin(28))
vb_pin = ADC(Pin(26))
pwm = PWM(Pin(9))
ina_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=2400000)
loop_timer = None

min_pwm = 9000
max_pwm = 42500
pwm_out = min_pwm

# Basic signals to control logic flow
global timer_elapsed
timer_elapsed = 0
count = 0
first_run = 1

# PID Gains for different power ranges
pid_gains = {
    "0-1": {"kp": 50, "ki": 5, "kd": 10},
    "1-2": {"kp": 25, "ki": 5, "kd": 10},
    "2-3": {"kp": 10, "ki": 5, "kd": 10},
}

# Initial PID Gains
kp, ki, kd = pid_gains["0-1"]["kp"], pid_gains["0-1"]["ki"], pid_gains["0-1"]["kd"]

# Control variables
v_err_int = 0
previous_v_err = 0
integral_min = -5000  # Minimum integral value
integral_max = 5000   # Maximum integral value

power_sum = 0
sample_count = 0
soc = 0

# Start with no energy stored (9000)
duty = int(min_pwm)
pwm.duty_u16(duty)

# Get initial desired power output
#P_desired = get_desired_power()

utime.sleep_ms(200)
P_desired = client.get_desired_power()
print(f"Desired Power: {P_desired}")

kp, ki, kd = update_pid_gains(P_desired, pid_gains)

# Initialize the PID controller
pid_controller = PIDController(kp, ki, kd, integral_min, integral_max)

def tick(t): 
    global timer_elapsed
    timer_elapsed = 1

while True:

    if first_run:
        # for first run, set up the INA link and the loop timer settings
        ina = INA219(SHUNT_OHMS, 64, 5)
        ina.configure()
        first_run = 0
        # This starts a 1kHz timer which we use to control the execution of the control loops and sampling
        loop_timer = Timer(mode=Timer.PERIODIC, freq=1000, callback=tick)        
    
    if timer_elapsed == 1: # This is executed at 1kHz
        timer_elapsed = 0  # Reset the timer flag

        va = 1.017 * (12490 / 2490) * 3.3 * (va_pin.read_u16() / 65536)  # Va calculation
        vb = 1.015 * (12490 / 2490) * 3.3 * (vb_pin.read_u16() / 65536)  # Vb calculation
        Vshunt = ina.vshunt()
        iL = -(Vshunt / SHUNT_OHMS)  # Invert the current sense for Boost

        # Calculate stored energy
        E_stored = round(0.5 * C * va**2 , 1)
        
        # Calculate power output
        power_output = va * iL

        # Limit charging when battery is near full capacity
        if (E_stored >= MAX_CAPACITY * 0.95 or soc >= 95) and P_desired >= 0:
            P_desired = 0.005

        # Limit discharging when battery is near empty
        if (E_stored <= 0.05 or soc <= 5) and P_desired < 0:
            P_desired = 0.005
        
        # Limit discharging when battery is near empty
        if P_desired == 0:
            # Scale P_desired based on SoC
            P_desired = 0.01 + soc/100 * (0.05 - 0.01)
            
        # PID Control
        error = P_desired - power_output
        pid_output = pid_controller.update(error)
        
        # Update the duty cycle
        duty += int(pid_output)
        duty = saturate(duty, max_pwm, min_pwm)

        pwm.duty_u16(duty)
        
        # Wait for stability
        utime.sleep_ms(5)
        
        # Calculate State of Charge (SoC)
        soc = calculate_soc(E_stored, MAX_CAPACITY)
        
        # Accumulate power for averaging
        power_sum += power_output
        sample_count += 1
        
        # Keep a count of how many times we have executed and reset the timer so we can go back to waiting
        count = count + 1
        timer_elapsed = 0
        
        if count % 25 == 0:
            # Print data in consistent format
            print(f"P:{power_output:.2f}, SoC:{soc:.2f}, iL:{iL:.2f}")

        # Check for new desired power output input and print average power every 5 seconds
        if count >= 1/5 * 1000:
            average_power = power_sum / sample_count
            print(f"Average Power over last 5 seconds: {average_power:.2f} W")
            
            P_desired = client.get_desired_power()
            print(f"Desired Power: {P_desired}")
            
            #P_desired = get_desired_power()
            kp, ki, kd = update_pid_gains(P_desired, pid_gains)  # Update PID gains based on new desired power
            pid_controller = PIDController(kp, ki, kd, integral_min, integral_max)
            power_sum = 0  # Reset power sum
            sample_count = 0  # Reset sample count
            count = 0