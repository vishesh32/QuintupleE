from machine import Pin, I2C, ADC, PWM, Timer
import utime

# Set up some pin allocations for the Analogues and switches
va_pin = ADC(Pin(28))
vb_pin = ADC(Pin(26))
ina_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=2400000)

# Some PWM settings, pin number, frequency, duty cycle limits and start with the PWM outputting the default of the min value.
min_pwm = 9000
max_pwm = 42500
pwm = PWM(Pin(9))
pwm.freq(100000)
pwm_out = min_pwm

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

# PID controller function
def pid_control(error):
    global prev_error
    global integral
    
    integral += error
    derivative = error - prev_error
    prev_error = error
    
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
