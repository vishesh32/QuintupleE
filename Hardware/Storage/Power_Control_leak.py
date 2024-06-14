from machine import Pin, I2C, ADC, PWM, Timer
import time, utime
import math
from mqtt_client import MClient, DEVICE

client = MClient(DEVICE.STORAGE)

# Initialization
va_pin = ADC(Pin(28))
ina_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=2400000)

pwm = PWM(Pin(9))
pwm.freq(100000)
min_pwm = 9000
max_pwm = 42300
pwm_out = min_pwm
duty = 0

C = 0.25  # Capacitance in Farads
SHUNT_OHMS = 0.10
max_capacity = 0.5 * C * 16 * 16
min_capacity = 0.5 * C * 7 * 7

# Basic signals to control logic flow
global timer_elapsed
timer_elapsed = 0
count = 0
first_run = 1

# PID Gains for different power ranges
pid_gains = {
    "0-1": {"kp": 50, "ki": 5, "kd": 10},    # Good enough
    "1-2": {"kp": 25, "ki": 5, "kd": 10},    # Test
    "2-3": {"kp": 10, "ki": 5, "kd": 10},    # Test
}

# PID Gains for SoC control
soc_pid_gains = {
    "default": {"kp": 1, "ki": 0, "kd": 0}  # Adjust these gains as needed
}

# Initial PID Gains
kp = pid_gains["0-1"]["kp"]
ki = pid_gains["0-1"]["ki"]
kd = pid_gains["0-1"]["kd"]

# Initial SoC PID Gains
soc_kp = soc_pid_gains["default"]["kp"]
soc_ki = soc_pid_gains["default"]["ki"]
soc_kd = soc_pid_gains["default"]["kd"]

# Control variables
v_err_int = 0
previous_v_err = 0
integral_min = -5000  # Minimum integral value
integral_max = 5000   # Maximum integral value

# Initialize the start time for power averaging
power_sum = 0
sample_count = 0
soc = 0
previous_soc = 0

soc_err_int = 0
previous_soc_err = 0
soc_integral_min = -5000  # Minimum integral value for SoC PID
soc_integral_max = 5000   # Maximum integral value for SoC PID

# Saturate function
def saturate(signal, upper, lower): 
    return max(min(signal, upper), lower)

# Timer callback function
def tick(t): 
    global timer_elapsed
    timer_elapsed = 1

# Class for INA219 current sensor
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


# Function to get user input for desired power output
def get_desired_power():
    while True:
        try:
            P_desired = float(input("Enter the desired power output in Watts: "))
            if abs(P_desired) <= 2:  # Limiting the absolute value of input to <= 4
                return P_desired
            else:
                print("Power output must be within +-3 Watts of the desired value.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

# Function to calculate State of Charge (SoC)
def calculate_soc(energy_stored):
    return min(100, max(0, (energy_stored - min_capacity) / (max_capacity - min_capacity) * 100))

# Function to update PID gains based on desired power
def update_pid_gains(P_desired):
    global kp, ki, kd
    if 0 <= abs(P_desired) <= 1:
        gains = pid_gains["0-1"]
    elif 1 < abs(P_desired) <= 2:
        gains = pid_gains["1-2"]
    elif 2 < abs(P_desired) <= 3:
        gains = pid_gains["2-3"]
    else:
        gains = pid_gains["0-1"]
    kp, ki, kd = gains["kp"], gains["ki"], gains["kd"]

# Function to update SoC PID gains
def update_soc_pid_gains():
    global soc_kp, soc_ki, soc_kd
    # You can define different SoC PID gains here based on your requirements
    soc_kp, soc_ki, soc_kd = soc_pid_gains["default"]["kp"], soc_pid_gains["default"]["ki"], soc_pid_gains["default"]["kd"]

# Function to calculate duty cycle from voltage using a quadratic equation
def duty_from_voltage(voltage):
    # Coefficients of the quadratic equation
    a = 6e-9
    b = -3e-5
    c = 7.1367 - voltage
    
    # Threshold voltage below which we return 9000
    threshold_voltage = 7.3527
    
    if voltage < threshold_voltage:
        return 9000
    
    # Calculate the discriminant
    discriminant = b**2 - 4 * a * c
    
    if discriminant < 0:
        raise ValueError("The equation has no real roots.")
    
    # Calculate the two possible solutions for x (duty)
    sqrt_discriminant = math.sqrt(discriminant)
    x1 = (-b + sqrt_discriminant) / (2 * a)
    x2 = (-b - sqrt_discriminant) / (2 * a)
    
    # Return the valid solution
    if x1 >= 0:
        return x1
    else:
        return x2

# 1 second delay to let storage voltage stabilize
utime.sleep_ms(1000)

# Calculate initial voltage and duty cycle
va = 1.017 * (12490 / 2490) * 3.3 * (va_pin.read_u16() / 65536)  # Va calculation
initial_voltage = va
print(f"Initial Va: {va}")
initial_duty = duty_from_voltage(initial_voltage)  # Calculate initial duty cycle
print(f"Initial Duty: {initial_duty}")
duty = int(initial_duty)
pwm.duty_u16(duty)


# Get initial desired power output
P_desired = 0
update_pid_gains(P_desired)

# Initialize INA219 and start the loop timer
ina = ina219(SHUNT_OHMS, 64, 5)
ina.configure()
loop_timer = Timer(mode=Timer.PERIODIC, freq=2000, callback=tick)

# Main control loop
while True:
    if timer_elapsed == 1:  # This is executed at 1kHz
        timer_elapsed = 0  # Reset the timer flag
        
        va = 1.017 * (12490 / 2490) * 3.3 * (va_pin.read_u16() / 65536)  # Va calculation
        Vshunt = ina.vshunt()
        iL = -(Vshunt / SHUNT_OHMS)  # Invert the current sense for Boost
        # Calculate power output
        power_output = va * iL

        # Calculate stored energy
        E_stored = round(0.5 * C * va**2 , 2)
        # Calculate State of Charge (SoC)
        soc = calculate_soc(E_stored)
        
        # Limit charging when battery is near full capacity
        if soc >= 90 and P_desired >= 0:
            P_desired = 0

        # Limit discharging when battery is near empty
        if soc <= 5 and P_desired < 0:
                P_desired = 0


        # Determine if we should switch to SoC control
        if P_desired == 0:
            if previous_soc == 0:
                previous_soc = soc
            # SoC Control
            soc_error = soc - previous_soc
            soc_err_int += soc_error
            soc_err_int = saturate(soc_err_int, soc_integral_max, soc_integral_min)
            soc_err_deriv = soc_error - previous_soc_err
            
            # Calculate the SoC PID output
            soc_pid_output = soc_kp * soc_error + soc_ki * soc_err_int + soc_kd * soc_err_deriv
            
            # Update duty cycle based on SoC PID output
            duty += int(soc_pid_output)
            duty = saturate(duty, max_pwm, min_pwm)
            
            # Update previous SoC error
            previous_soc_err = soc_error
            
        else:
            previous_soc = 0
            # Power Control (as before)
            error = P_desired - power_output
            v_err_int += error
            v_err_int = saturate(v_err_int, integral_max, integral_min)
            v_err_deriv = error - previous_v_err
            
            # Calculate the PID output for power control
            pid_output = kp * error + ki * v_err_int + kd * v_err_deriv
            
            # Update duty cycle based on power PID output
            duty += int(pid_output)
            duty = saturate(duty, max_pwm, min_pwm)
            
            # Update previous power error
            previous_v_err = error
        
        pwm.duty_u16(duty)
        utime.sleep_ms(5)
        
        # Accumulate power for averaging
        power_sum += power_output
        sample_count += 1
        
        count += 1
        
        if count % 25 == 0:
            # Print data in consistent format
            print(f"P: {power_output:.2f}, SoC: {soc:.2f}, iL: {iL*1000:.2f}, T: {count//200}")
        
        # Check for new desired power output input and print average power every 5 seconds
        if count >= 1000:
            average_power = power_sum / sample_count
            print(f"Average Power over last 5 seconds: {average_power:.2f} W")

            P_desired = get_desired_power()
            update_pid_gains(P_desired)

            power_sum = 0  # Reset power sum
            sample_count = 0  # Reset sample count
            count = 0

            client.send_storage_power(average_power)
            client.send_soc(soc)

