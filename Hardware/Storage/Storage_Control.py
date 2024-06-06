from machine import Pin, I2C, ADC, PWM, Timer
import time, utime

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


# Basic signals to control logic flow
global timer_elapsed
timer_elapsed = 0
count = 0
first_run = 1

# Need to know the shunt resistance to calculate the current
global SHUNT_OHMS
SHUNT_OHMS = 0.10


# Initialize variables for energy tracking
energy_stored = 6.4  # Initial energy stored
energy_max = 31.4  # Maximum energy
energy_min = 0  # Minimum energy
energy_target = 25  # Target energy
energy_change_per_tick = 2.5  # Energy change per tick (5 seconds)
ticks_to_release = 10  # Total ticks to release energy
tick_duration = 5000  # Tick duration in milliseconds

# Initialize PID controller parameters
kp = 0.1  # Proportional gain
ki = 0.01  # Integral gain
kd = 0  # Derivative gain
prev_error = 0
integral = 0


# saturation function for anything you want saturated within bounds
def saturate(signal, upper, lower): 
    if signal > upper:
        signal = upper
    if signal < lower:
        signal = lower
    return signal

# This is the function executed by the loop timer, it simply sets a flag which is used to control the main loop
def tick(t): 
    global timer_elapsed
    timer_elapsed = 1

# Define functions
def change_energy():
    global energy_stored
    global energy_max
    global energy_min
    
    while True:
        try:
            energy_change = float(input("Enter energy change (+ for charge, - for discharge): "))
            if energy_change > 0:
                energy_stored = min(energy_stored + energy_change, energy_max)
            else:
                energy_stored = max(energy_stored + energy_change, energy_min)
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")

# These functions relate to the configuring of and reading data from the INA219 Current sensor
class ina219: 
    
    # Register Locations
    REG_CONFIG = 0x00
    REG_SHUNTVOLTAGE = 0x01
    REG_BUSVOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05
    
    def __init__(self,sr, address, maxi):
        self.address = address
        self.shunt = sr
            
    def vshunt(icur):
        # Read Shunt register 1, 2 bytes
        reg_bytes = ina_i2c.readfrom_mem(icur.address, icur.REG_SHUNTVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big')
        if reg_value > 2**15: #negative
            sign = -1
            for i in range(16): 
                reg_value = (reg_value ^ (1 << i))
        else:
            sign = 1
        return (float(reg_value) * 1e-5 * sign)
        
    def vbus(ivolt):
        # Read Vbus voltage
        reg_bytes = ina_i2c.readfrom_mem(ivolt.address, ivolt.REG_BUSVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big') >> 3
        return float(reg_value) * 0.004
        
    def configure(conf):
        #ina_i2c.writeto_mem(conf.address, conf.REG_CONFIG, b'\x01\x9F') # PG = 1
        #ina_i2c.writeto_mem(conf.address, conf.REG_CONFIG, b'\x09\x9F') # PG = /2
        ina_i2c.writeto_mem(conf.address, conf.REG_CONFIG, b'\x19\x9F') # PG = /8
        ina_i2c.writeto_mem(conf.address, conf.REG_CALIBRATION, b'\x00\x00')


# Set duty cycle to min_pwm
pwm_out = min_pwm
pwm_out = saturate(pwm_out, max_pwm, min_pwm)
pwm.duty_u16(int(pwm_out))

# Wait for 5 seconds
utime.sleep_ms(5000)

# Open a file in write mode and write the header row
with open('Capacitor_Data.csv', 'w') as f:
    f.write('Va,Vb,iL,Po,Duty,Time(ms)\n')
    
    start_time = utime.ticks_ms()

    while True:
        va = 1.017*(12490/2490)*3.3*(va_pin.read_u16()/65536) # calibration factor * potential divider ratio * ref voltage * digital reading
        vb = 1.015*(12490/2490)*3.3*(vb_pin.read_u16()/65536) # calibration factor * potential divider ratio * ref voltage * digital reading
        Vshunt = ina219.vshunt()
        iL = -(Vshunt/SHUNT_OHMS) # Invert the current sense for Boost

        # Ask user for energy change
        change_energy()
        
        # PID controller for duty cycle
        error = energy_target - energy_stored
        integral += error
        derivative = error - prev_error
        pid_output = kp * error + ki * integral + kd * derivative
        pid_output = saturate(pid_output, 3500, -3500)  # Limit maximum change to prevent spikes
        
        # Update duty cycle
        pwm_out += pid_output
        pwm_out = saturate(pwm_out, max_pwm, min_pwm)
        duty = int(pwm_out)
        pwm.duty_u16(duty)
        
        # Record current time and calculate elapsed time
        current_time = utime.ticks_ms()
        elapsed_time = utime.ticks_diff(current_time, start_time) // 1000
        
        # Calculate output power (Va * iL)
        output_power = va * iL  

        # Update energy stored
        energy_stored += energy_change_per_tick
        energy_stored = max(energy_min, min(energy_stored, energy_max))
        
        # Print and record data
        print("Va = {:.3f} V".format(va))
        print("Vb = {:.3f} V".format(vb))
        print("iL = {:.3f} A".format(iL))
        print("Po = {:.3f} W".format(output_power))
        print("Duty = {:d}".format(duty))
        print("Time = {:d}".format(elapsed_time))
        print("Energy = {:.2f} J".format(energy_stored))
        print(" ")
        f.write(f'{va:.3f},{vb:.3f},{iL:.3f},{output_power:.3f},{duty},{elapsed_time},{energy_stored:.2f}\n')
        

        # Check if energy change exceeds limits
        if energy_stored < 6.4:
            print("Warning: Energy cannot go below 6.4J.")
            energy_stored = 6.4
        elif energy_stored > 25:
            print("Warning: Energy cannot exceed 25J.")
            energy_stored = 25


        # Check if it's time to release energy
        if elapsed_time % tick_duration == 0 and elapsed_time != 0:
            # Calculate the energy to be released in this tick
            energy_to_release = min(energy_change_per_tick, energy_stored)
            
            # Update the energy stored
            energy_stored -= energy_to_release
            
            # Ensure energy remains within bounds
            energy_stored = max(energy_min, min(energy_stored, energy_max))

        # Sleep before next iteration
        utime.sleep_ms(100)