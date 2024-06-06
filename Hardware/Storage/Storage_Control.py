from machine import Pin, ADC, PWM, Timer
import utime

# Set up pin for the analogue voltage reading
va_pin = ADC(Pin(28))

# PWM settings
min_pwm = 9000
max_pwm = 42500
pwm = PWM(Pin(9))
pwm.freq(100000)
pwm_out = min_pwm

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

# PID controller function
def pid_control(error):
    global prev_error
    global integral
    
    integral += error
    derivative = error - prev_error
    prev_error = error
    
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
