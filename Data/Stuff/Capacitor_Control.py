from machine import Pin, I2C, ADC, PWM, Timer
import utime

# Set up some pin allocations for the Analogues and switches
va_pin = ADC(Pin(28))
vb_pin = ADC(Pin(26))
vpot_pin = ADC(Pin(27))
OL_CL_pin = Pin(12, Pin.IN, Pin.PULL_UP)
BU_BO_pin = Pin(2, Pin.IN, Pin.PULL_UP)

# Set up the I2C for the INA219 chip for current sensing
ina_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=2400000)

# Some PWM settings, pin number, frequency, duty cycle limits and start with the PWM outputting the default of the min value.
pwm = PWM(Pin(9))
pwm.freq(100000)
min_pwm = 9000
max_pwm = 42500
pwm_out = min_pwm
pwm_ref = 30000

# Some error signals
trip = 0
OC = 0

# Gains etc for the PID controller
v_ref = 0  # Voltage reference for the CL modes
v_err = 0  # Voltage error
v_err_int = 0  # Voltage error integral
v_pi_out = 0  # Output of the voltage PI controller
kp = 100  # Boost Proportional Gain
ki = 30  # Boost Integral Gain

# Basic signals to control logic flow
global timer_elapsed
timer_elapsed = 0
count = 0
first_run = 1

# Need to know the shunt resistance to calculate the current
global SHUNT_OHMS
SHUNT_OHMS = 0.10
global CAPACITANCE
CAPACITANCE = 0.25  # Example value, set this to the actual capacitance

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

# Function to calculate current energy based on duty cycle
def duty_to_energy(duty):
    return -8e-18 * duty**4 + 1e-12 * duty**3 - 4e-8 * duty**2 + 0.0008 * duty + 1.8256

# Function to calculate duty cycle based on energy
def energy_to_duty(energy):
    return int(-0.1236 * energy**4 + 12.178 * energy**3 - 453.86 * energy**2 + 8318 * energy - 28400)

# Set initial duty cycle
pwm_out = min_pwm
# Initialize energy stored in the capacitor
current_energy = duty_to_energy(pwm_out)
current_energy = round(current_energy, 2)

duty = int(pwm_out)
pwm.duty_u16(duty)

utime.sleep_ms(4500)

# Here we go, main function, always executes
while True:
    if first_run:
        # for first run, set up the INA link and the loop timer settings
        ina = ina219(SHUNT_OHMS, 64, 5)
        ina.configure()
        first_run = 0
        
        # This starts a 1kHz timer which we use to control the execution of the control loops and sampling
        loop_timer = Timer(mode=Timer.PERIODIC, freq=1000, callback=tick)
    
    # If the timer has elapsed it will execute some functions, otherwise it skips everything and repeats until the timer elapses
    if timer_elapsed == 1:  # This is executed at 1kHz
        va = 1.017 * (12490 / 2490) * 3.3 * (va_pin.read_u16() / 65536)  # calibration factor * potential divider ratio * ref voltage * digital reading
        vb = 1.015 * (12490 / 2490) * 3.3 * (vb_pin.read_u16() / 65536)  # calibration factor * potential divider ratio * ref voltage * digital reading
        
        Vshunt = ina.vshunt()
        
        # Boost uses different limits on the PWM (why?) and inverts the current (also why?)
        min_pwm = 9000
        max_pwm = 42500  # limit the duty in boost mode to prevent high voltages
        iL = -(Vshunt / SHUNT_OHMS)  # Invert the current sense for Boost
        
        # Saturate the pwm and send it out (not inverted because boost)    
        pwm_out = saturate(pwm_out, max_pwm, min_pwm)
        duty = int(pwm_out)
        pwm.duty_u16(duty)
        

    timer_elapsed = 0

    # Prompt the user for input and adjust duty cycle to achieve the desired change in energy
    delta_energy = float(input("Enter the change in energy: "))  # Prompt user for input

    # Calculate new energy based on current energy and delta
    new_energy = current_energy + delta_energy
    new_energy = round(new_energy, 2)
    
    # Limit the new energy to the maximum and minimum energy thresholds
    new_energy = min(new_energy, 31.4)  # Maximum energy threshold
    new_energy = max(new_energy, 6.4)   # Minimum energy threshold


    # Calculate new duty cycle based on new energy
    new_duty = energy_to_duty(new_energy)

    # Calculate step size
    total_steps = 100  # Total number of steps to reach the new duty cycle
    step_duration = 450  # Time duration (ms) for each step
    current_duty = pwm_out
    duty_difference = new_duty - current_duty
    max_step_size = 4000  # Maximum allowed step size

    # Calculate step size, ensuring a minimum increment of 1 and a maximum of 3000
    step_size = max(415, min(max_step_size, duty_difference // total_steps))

    # Adjust duty cycle and track changes until current energy is close to the desired energy
    while True:
        # Increment or decrement the current duty by the step size
        if new_duty > current_duty:
            current_duty += step_size
            if current_duty > new_duty:
                current_duty = new_duty
        else:
            current_duty -= step_size
            if current_duty < new_duty:
                current_duty = new_duty

        # Saturate the duty cycle and set it
        pwm_out = saturate(current_duty, max_pwm, min_pwm)
        duty = int(pwm_out)
        pwm.duty_u16(duty)

        # Read values and calculate current energy
        va = 1.017 * (12490 / 2490) * 3.3 * (va_pin.read_u16() / 65536)
        vb = 1.015 * (12490 / 2490) * 3.3 * (vb_pin.read_u16() / 65536)
        Vshunt = ina.vshunt()
        iL = -(Vshunt / SHUNT_OHMS)
        current_energy = 0.5 * CAPACITANCE * va**2
        current_energy = round(current_energy, 2)

        # Print real-time values
        print(f"Va = {va:.1f} V, iL = {iL:.3f} A, Duty = {duty}, New Energy = {new_energy:.1f},Current Energy = {current_energy:.1f} J")

        # Check if current energy is nearly equal to the desired new energy
        if abs(current_energy - new_energy) < 0.25:  # Adjust tolerance as needed
            break

        # Sleep for the duration of each step
        utime.sleep_ms(step_duration)

    # Ensure the final duty cycle matches the desired duty cycle
    pwm_out = new_duty
    duty = int(pwm_out)
    pwm.duty_u16(duty)

    # Update current energy
    current_energy = duty_to_energy(duty)
    
    print("\nEnergy Change Complete!\n")



