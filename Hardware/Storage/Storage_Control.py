<<<<<<< HEAD
from machine import Pin, I2C, ADC, PWM, Timer
=======
from machine import Pin, ADC, PWM, Timer
>>>>>>> a39d187573bcd1a959876119a55949c9ed3dfa72
import utime

# Set up pin for the analogue voltage reading
va_pin = ADC(Pin(28))

# PWM settings
min_pwm = 9000
max_pwm = 42500
pwm = PWM(Pin(9))
pwm.freq(100000)
pwm_out = min_pwm

<<<<<<< HEAD
# Constants
C = 0.25  # Capacitance in Farads
V_min = 7  # Minimum voltage in Volts
V_max = 16  # Maximum voltage in Volts
global SHUNT_OHMS
SHUNT_OHMS = 0.10

# Initialize variables for energy tracking
energy_stored_actual = 0.5 * C * V_min**2  # Initial energy stored in Joules (6.4J)
energy_max_actual = 0.5 * C * V_max**2  # Maximum energy in Joules (31.4J)
energy_min_actual = 0  # Minimum usable energy (0J)
energy_target = energy_stored_actual  # Target energy initially same as initial stored energy
energy_change_per_tick = 2.5  # Energy change per tick (5 seconds)
tick_duration = 5000  # Tick duration in milliseconds

# Initialize PID controller parameters
kp = 25  # Proportional gain
ki = 75  # Integral gain
kd = 0  # Derivative gain
prev_error = 0
integral = 0

# Stabilization variables
stabilization_time = 200  # Time to wait for voltage to stabilize in ms
voltage_tolerance = 0.05  # Voltage tolerance for stabilization

# Saturation function for anything you want saturated within bounds
def saturate(signal, upper, lower): 
    return min(max(signal, lower), upper)

=======
# Capacitor parameters
C = 0.25  # Capacitance in Farads
V_min = 6  # Minimum voltage in Volts
V_max = 16  # Maximum voltage in Volts

# Constants for voltage stabilization
stabilization_factor = 2  # Time per Joule for stabilization in milliseconds

# PID parameters
kp = 0.5  # Proportional gain
ki = 0.01  # Integral gain
kd = 0.01  # Derivative gain

# Initialize variables
energy_target = 0
voltage_target = V_min
voltage_estimate = V_min
prev_voltage_estimate = V_min
prev_error = 0
integral = 0

# Saturation function for duty cycle
def saturate(signal, upper, lower):
    return min(max(signal, lower), upper)

# Function to estimate duty cycle based on energy
def duty_from_energy(energy):
    return (-0.1236 * energy**4) + (12.178 * energy**3) - (453.86 * energy**2) + (8318 * energy) - 28751

# Function to estimate duty cycle based on voltage
def duty_from_voltage(voltage):
    return (36.113 * voltage**3) - (1529.6 * voltage**2) + (23997 * voltage) - 98089

>>>>>>> a39d187573bcd1a959876119a55949c9ed3dfa72
# PID controller function
def pid_control(error):
    global prev_error
    global integral
    
    integral += error
    derivative = error - prev_error
    prev_error = error
<<<<<<< HEAD
    
    pid_output = kp * error + ki * integral + kd * derivative
    return saturate(pid_output, 500, -500)  # Limit maximum change to prevent spikes

# Wait for stabilization function
def wait_for_stabilization(set_voltage):
    while True:
        va = 1.017*(12490/2490)*3.3*(va_pin.read_u16()/65536)  # Read voltage from pin
        if abs(va - set_voltage) < voltage_tolerance:
            break
        utime.sleep_ms(10)  # Wait for 10ms and check again

# Main loop
while True:
    start_time = utime.ticks_ms()  # Track start time
    
    while utime.ticks_diff(utime.ticks_ms(), start_time) < tick_duration:
        # Read current voltage
        va = 1.017*(12490/2490)*3.3*(va_pin.read_u16()/65536)  # Read voltage from pin
        
        # Calculate energy stored based on voltage
        energy_stored_actual = 0.5 * C * va**2
        
        # PID controller
        error = energy_target - energy_stored_actual
        pid_output = pid_control(error)
        
        # Update duty cycle
        pwm_out += pid_output
        pwm_out = saturate(pwm_out, max_pwm, min_pwm)
        pwm.duty_u16(int(pwm_out))
        
        # Wait for stabilization of voltage
        wait_for_stabilization(va)
        
        # Print and record data
        print("Va = {:.3f} V".format(va))
        print("Energy = {:.2f} J".format(energy_stored_actual))
        print(" ")
        
        utime.sleep_ms(100)  # Small delay before next iteration of the loop
    
    # Ask user for new energy change after every 5-second tick period
    energy_change = float(input("Enter energy change (+ for charge, - for discharge): "))
    energy_target += energy_change
=======
    
    pid_output = kp * error + ki * integral + kd * derivative
    return saturate(pid_output, 500, -500)  # Limit maximum change to prevent spikes

# Function to wait for voltage stabilization
def wait_for_stabilization(set_voltage):
    stabilization_time = stabilization_factor * abs(voltage_estimate - set_voltage)
    utime.sleep_ms(stabilization_time)

# Main loop
while True:
    # Read current voltage
    va = 1.017 * (12490 / 2490) * 3.3 * (va_pin.read_u16() / 65536)  # Read voltage from pin
    
    # Estimate current energy stored
    energy_stored = 0.5 * C * va**2
    
    # Calculate error for PID control
    error = voltage_target - voltage_estimate
    
    # PID control
    pid_output = pid_control(error)
    pwm_out += pid_output
    pwm_out = saturate(pwm_out, max_pwm, min_pwm)
    pwm.duty_u16(int(pwm_out))
    
    # Wait for voltage stabilization
    wait_for_stabilization(voltage_target)
    
    # Update voltage estimate
    prev_voltage_estimate = voltage_estimate
    voltage_estimate = va
    
    # Print status
    print("Current Voltage: {:.2f} V".format(va))
    print("Energy Stored: {:.2f} J".format(energy_stored))
    print(" ")

    # Check if the current desired energy change has been completed
    if energy_stored == energy_target:
        # User input for new energy change
        energy_change = float(input("Enter energy change (+ for charge, - for discharge): "))
        energy_target += energy_change
    
        # Update voltage target based on new energy target
        voltage_target = ((2 * energy_target) / C) ** 0.5
        if voltage_target < V_min:
            voltage_target = V_min
        elif voltage_target > V_max:
            voltage_target = V_max
>>>>>>> a39d187573bcd1a959876119a55949c9ed3dfa72
