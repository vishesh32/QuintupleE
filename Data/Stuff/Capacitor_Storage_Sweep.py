from machine import Pin, I2C, ADC, PWM, Timer
import time, utime

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
min_pwm = 1000
max_pwm = 64536
pwm_out = min_pwm
pwm_ref = 30000

#Some error signals
trip = 0
OC = 0

# The potentiometer is prone to noise so we are filtering the value using a moving average
v_pot_filt = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
v_pot_index = 0

# Gains etc for the PID controller
v_ref = 0 # Voltage reference for the CL modes
v_err = 0 # Voltage error
v_err_int = 0 # Voltage error integral
v_pi_out = 0 # Output of the voltage PI controller
kp = 100 # Boost Proportional Gain
ki = 30 # Boost Integral Gain

# Basic signals to control logic flow
global timer_elapsed
timer_elapsed = 0
count = 0
first_run = 1

# Need to know the shunt resistance to calculate the current
global SHUNT_OHMS
SHUNT_OHMS = 0.10

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


# Set initial duty cycle
pwm_out = max_pwm

# Sweep direction
sweep_direction = -1  # 1 for increasing, -1 for decreasing

# Open a file in write mode and write the header row
with open('Capacitor_Data.csv', 'w') as f:
    f.write('Va,Vb,iL,Po,Duty,Time(ms)\n')

    # Initialize the start time
    start_time = utime.ticks_ms()

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
        if timer_elapsed == 1: # This is executed at 1kHz
            va = 1.017*(12490/2490)*3.3*(va_pin.read_u16()/65536) # calibration factor * potential divider ratio * ref voltage * digital reading
            vb = 1.015*(12490/2490)*3.3*(vb_pin.read_u16()/65536) # calibration factor * potential divider ratio * ref voltage * digital reading
            
            Vshunt = ina.vshunt()
            
            # Boost uses different limits on the PWM (why?) and inverts the current (also why?)
            min_pwm = 2000
            max_pwm = 42500 # limit the duty in boost mode to prevent high voltages
            iL = -(Vshunt/SHUNT_OHMS) # Invert the current sense for Boost
            
            # Set up the reference PWM directly based on the sweep
            pwm_out += 100  # Increment PWM duty by 100 each time
            
            # Saturate the pwm and send it out (not inverted because boost)    
            pwm_out = saturate(pwm_out, max_pwm, min_pwm)
            duty = int(pwm_out)
            pwm.duty_u16(duty)
                
                
        # Keep a count of how many times we have executed and reset the timer so we can go back to waiting
        count = count + 1
        timer_elapsed = 0

        
        # This set of prints executes every 1 loops by default and can be used to output debug or extra info over USB enable or disable lines as needed
        if count > 1:
            output_power = va * iL  # Calculate output power (Va * iL)
            
            # Record the current time and calculate the elapsed time
            current_time = utime.ticks_ms()
            elapsed_time = utime.ticks_diff(current_time, start_time)//1000
            
            print("Va = {:.3f} V".format(va))
            print("Vb = {:.3f} V".format(vb))
            print("iL = {:.3f} A".format(iL))
            print("Po = {:.3f} W".format(output_power))
            print("Duty = {:d}".format(duty))
            print("Time = {:d}".format(elapsed_time))
            print(" ")
            
            # Write the data to the CSV file with the elapsed time
            f.write(f'{va:.3f},{vb:.3f},{iL:.3f},{output_power:.3f},{duty},{elapsed_time}\n')
            
            count = 0

        # Sweep the duty cycle gradually
        pwm_out += sweep_direction * 1000  # Increment by 1000
        if pwm_out <= min_pwm:
            pwm_out = min_pwm  # Stop at the minimum PWM value
            sweep_direction = 0  # Stop sweeping
        
        utime.sleep_ms(7500)
