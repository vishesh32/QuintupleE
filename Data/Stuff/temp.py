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
min_pwm = 1000
max_pwm = 64536
pwm_out = min_pwm
pwm_ref = 30000

# Some error signals
trip = 0
OC = 0

# The potentiometer is prone to noise so we are filtering the value using a moving average
v_pot_filt = [0] * 100
v_pot_index = 0

# Gains etc for the PID controller
i_ref = 0  # Voltage reference for the CL modes
i_err = 0  # Voltage error
i_err_int = 0  # Voltage error integral
i_pi_out = 0  # Output of the voltage PI controller
kp = 100  # Boost Proportional Gain
ki = 300  # Boost Integral Gain

# Basic signals to control logic flow
global timer_elapsed
timer_elapsed = 0
count = 0
first_run = 1

# Need to know the shunt resistance
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
    
    def __init__(self, sr, address, maxi):
        self.address = address
        self.shunt = sr
            
    def vshunt(self):
        # Read Shunt register 1, 2 bytes
        reg_bytes = ina_i2c.readfrom_mem(self.address, self.REG_SHUNTVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big')
        if reg_value > 2**15:  # negative
            sign = -1
            for i in range(16):
                reg_value = (reg_value ^ (1 << i))
        else:
            sign = 1
        return (float(reg_value) * 1e-5 * sign)
        
    def vbus(self):
        # Read Vbus voltage
        reg_bytes = ina_i2c.readfrom_mem(self.address, self.REG_BUSVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big') >> 3
        return float(reg_value) * 0.004
        
    def configure(self):
        #ina_i2c.writeto_mem(self.address, self.REG_CONFIG, b'\x01\x9F')  # PG = 1
        #ina_i2c.writeto_mem(self.address, self.REG_CONFIG, b'\x09\x9F')  # PG = /2
        ina_i2c.writeto_mem(self.address, self.REG_CONFIG, b'\x19\x9F')  # PG = /8
        ina_i2c.writeto_mem(self.address, self.REG_CALIBRATION, b'\x00\x00')


# Variables for Incremental Conductance
prev_va = 0
prev_iL = 0
current_duty = min_pwm
step = 1000

# Open a CSV file for writing
with open('/IC_Data.csv', 'w') as file:
    file.write('Time,Duty Cycle,Va,Vb,iL,Po,IncrCond\n')  # Write the header row
    
    start_time = utime.ticks_ms()  # Get the starting time in milliseconds

    # Here we go, main function, always executes
    while True:
        current_time = utime.ticks_ms()  # Get the current time in milliseconds
        elapsed_time = (current_time - start_time) / 1000  # Convert to seconds

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
            
            vpot_in = 1.026 * 3.3 * (vpot_pin.read_u16() / 65536)  # calibration factor * potential divider ratio * ref voltage * digital reading
            v_pot_filt[v_pot_index] = vpot_in  # Adds the new reading to our array of readings at the current index
            v_pot_index = (v_pot_index + 1) % 100  # Moves the index of the buffer for next time
            vpot = sum(v_pot_filt) / 100  # Actual reading used is the average of the last 100 readings
            
            Vshunt = ina.vshunt()
            CL = OL_CL_pin.value()  # Are we in closed or open loop mode
            BU = BU_BO_pin.value()  # Are we in buck or boost mode?
            
            # New min and max PWM limits and we use the measured current directly
            min_pwm = 1000
            max_pwm = 64536
            iL = Vshunt / SHUNT_OHMS
            pwm_ref = saturate(65536 - int((vpot / 3.3) * 65536), max_pwm, min_pwm)  # convert the pot value to a PWM value for use later

            i_ref = saturate(vpot - 1.66, 1.5, -1.5)
            i_err = i_ref - iL  # calculate the error in voltage
            i_err_int = i_err_int + i_err  # add it to the integral error
            i_err_int = saturate(i_err_int, 10000, -10000)  # saturate the integral error
            i_pi_out = (kp * i_err) + (ki * i_err_int)  # Calculate a PI controller output
            
            pwm_out = saturate(i_pi_out, max_pwm, min_pwm)  # Saturate that PI output
            duty = int(65536 - pwm_out)  # Invert because reasons
            pwm.duty_u16(duty)  # Send the output of the PI controller out as PWM

            # Incremental Conductance Algorithm
            delta_iL = iL - prev_iL
            delta_va = va - prev_va
            
            if delta_va != 0:
                incremental_conductance = delta_iL / delta_va
                instantaneous_conductance = -iL / va

                if incremental_conductance == instantaneous_conductance:
                    # At MPP, no change needed
                    pass
                elif incremental_conductance > instantaneous_conductance:
                    # To the left of MPP, increase voltage (decrease duty cycle)
                    current_duty -= step
                else:
                    # To the right of MPP, decrease voltage (increase duty cycle)
                    current_duty += step
            
            # Ensure the duty cycle stays within bounds
            current_duty = saturate(current_duty, max_pwm, min_pwm)
            duty = 65536 - current_duty  # Invert because of hardware requirements
            pwm.duty_u16(duty)  # Set the PWM duty cycle
            
            # Update previous values for next iteration
            prev_va = va
            prev_iL = iL

            # Calculate output power
            output_power = vb * iL  # Calculate output power (Va * iL)

            # Write data to the CSV file
            file.write(f"{elapsed_time:.2f},{current_duty},{va:.3f},{vb:.3f},{iL:.3f},{output_power:.3f},{incremental_conductance:.3f}\n")

            # Keep a count of how many times we have executed and reset the timer so we can go back to waiting
            count += 1
            timer_elapsed = 0

            # This set of prints executes every 100 loops by default and can be used to output debug or extra info over USB enable or disable lines as needed
            if count > 1:
                print(f"Time = {elapsed_time:.2f}s, Po = {output_power:.5f} W, IncrCond = {incremental_conductance:.5f} A/V, duty = {duty}")
                count = 0
