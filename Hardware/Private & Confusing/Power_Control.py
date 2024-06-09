from machine import Pin, I2C, ADC, PWM, Timer
import time, utime

# Initialization
va_pin = ADC(Pin(28))
vb_pin = ADC(Pin(26))
ina_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=2400000)

pwm = PWM(Pin(9))
pwm.freq(100000)
min_pwm = 9000
max_pwm = 42300
pwm_out = min_pwm

C = 0.25  # Capacitance in Farads
SHUNT_OHMS = 0.10

# Basic signals to control logic flow
global timer_elapsed
timer_elapsed = 0
count = 0
first_run = 1

# PID Gains for different power ranges
pid_gains = {
    "0-1": {"kp": 2000, "ki": 500, "kd": 30},
    "1-2": {"kp": 1500, "ki": 300, "kd": 20},
    "2-3": {"kp": 1000, "ki": 200, "kd": 15},
    "3-4": {"kp": 500, "ki": 100, "kd": 10}
}

# Initial PID Gains
kp = pid_gains["0-1"]["kp"]
ki = pid_gains["0-1"]["ki"]
kd = pid_gains["0-1"]["kd"]

# Control variables
v_err_int = 0
previous_v_err = 0
integral_min = -5000  # Minimum integral value
integral_max = 5000   # Maximum integral value

# Tolerance for error
stability_threshold = 0.005  # Reduced Stability Threshold
stability_samples = 25
stability_wait_time = 250  # Reduced Stability Wait Time

# Saturate function
def saturate(signal, upper, lower): 
    return max(min(signal, upper), lower)

# This is the function executed by the loop timer, it simply sets a flag which is used to control the main loop
def tick(t): 
    global timer_elapsed
    timer_elapsed = 1

class ina219: 
    # Register Locations
    REG_CONFIG = 0x00
    REG_SHUNTVOLTAGE = 0x01
    REG_BUSVOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05
    
    def __init__(self, sr, address, maxi):
        self.address = address
        self.shunt = sr
            
    def vshunt(self):
        # Read Shunt register 1, 2 bytes
        reg_bytes = ina_i2c.readfrom_mem(self.address, self.REG_SHUNTVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big')
        if reg_value > 2**15: #negative
            sign = -1
            for i in range(16): 
                reg_value = (reg_value ^ (1 << i))
        else:
            sign = 1
        return float(reg_value) * 1e-5 * sign
        
    def vbus(self):
        # Read Vbus voltage
        reg_bytes = ina_i2c.readfrom_mem(self.address, self.REG_BUSVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big') >> 3
        return float(reg_value) * 0.004
        
    def configure(self):
        ina_i2c.writeto_mem(self.address, self.REG_CONFIG, b'\x19\x9F') # PG = /8
        ina_i2c.writeto_mem(self.address, self.REG_CALIBRATION, b'\x00\x00')

# Function to wait until voltage stabilizes with averaging
def wait_for_stability():
    stable = False
    samples = []
    for _ in range(stability_samples):
        current_va = va_pin.read_u16() / 65536 * 3.3
        samples.append(current_va)
        utime.sleep_ms(stability_wait_time // stability_samples)
    avg_va = sum(samples) / len(samples)
    max_diff = max(abs(v - avg_va) for v in samples)
    if max_diff < stability_threshold:
        stable = True
    return stable

# Function to get user input for desired power output
def get_desired_power():
    while True:
        try:
            P_desired = float(input("Enter the desired power output in Watts: "))
            return P_desired
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

# Function to calculate State of Charge (SoC)
def calculate_soc(energy_stored):
    max_capacity = 25.0  # Maximum capacity in Joules
    return min(100, max(0, (energy_stored - 6.4) / (max_capacity - 6.4) * 100))

# Function to update PID gains based on desired power
def update_pid_gains(P_desired):
    global kp, ki, kd
    if 0 <= abs(P_desired) < 1:
        gains = pid_gains["0-1"]
    elif 1 <= abs(P_desired) < 2:
        gains = pid_gains["1-2"]
    elif 2 <= abs(P_desired) < 3:
        gains = pid_gains["2-3"]
    elif 3 <= abs(P_desired) <= 4:
        gains = pid_gains["3-4"]
    else:
        gains = pid_gains["0-1"]
    kp, ki, kd = gains["kp"], gains["ki"], gains["kd"]

# Start with no energy stored (9000)
duty = int(min_pwm)
pwm.duty_u16(duty)

# Get initial desired power output
P_desired = get_desired_power()
update_pid_gains(P_desired)

# Initialize the start time
start_time = utime.ticks_ms()
power_sum = 0
sample_count = 0

previous_input = None  # Variable to store the previous input

while True:
    if first_run:
        # for first run, set up the INA link and the loop timer settings
        ina = ina219(SHUNT_OHMS, 64, 5)
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
        
        # PID Control
        error = P_desired - power_output
        v_err_int += error  # Integrate the error
        v_err_int = saturate(v_err_int, integral_max, integral_min)  # Clamp the integral term
        v_err_deriv = error - previous_v_err  # Calculate the derivative of the error
        
        # Calculate the PID output
        pid_output = kp * error + ki * v_err_int + kd * v_err_deriv
        
        # Update the duty cycle
        duty += int(pid_output)
        duty = saturate(duty, max_pwm, min_pwm)

        # Update the previous error
        previous_v_err = error

        # Safety feature: If Va crosses 16V, set duty to 42500
        if va > 16.0:
            duty = 42300

        pwm.duty_u16(duty)
        
        wait_for_stability()

        # Calculate State of Charge (SoC)
        soc = calculate_soc(E_stored)
        
        # Accumulate power for averaging
        power_sum += power_output
        sample_count += 1
        
        # Print data in consistent format
        current_time = utime.ticks_ms()
        elapsed_time = utime.ticks_diff(current_time, start_time)
        print(f"P: {power_output*10:.2f} dW, SoC: {soc:.2f}%, T: {elapsed_time//1000} ms")

        # Check for new desired power output input and print average power every 5 seconds
        if elapsed_time >= 5*1000:
            average_power = power_sum / sample_count
            print(f"Average Power over last 5 seconds: {average_power:.2f} W")
            P_desired = get_desired_power()
            update_pid_gains(P_desired)  # Update PID gains based on new desired power
            start_time = utime.ticks_ms()  # Reset the start time
            power_sum = 0  # Reset power sum
            sample_count = 0  # Reset sample count
            start_time = utime.ticks_ms()  # Reset the start time
