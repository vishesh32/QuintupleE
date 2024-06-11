from machine import Pin, I2C, ADC, PWM, Timer
import time, utime

# Constants
MIN_PWM = 9000
MAX_PWM = 42300
SHUNT_OHMS = 0.10
MAX_CAPACITY = 21.0
STABILITY_THRESHOLD = 0.005
STABILITY_SAMPLES = 10
STABILITY_WAIT_TIME = 150
POWER_UPDATE_INTERVAL = 1000

# Global Variables
timer_elapsed = 0
count = 0
first_run = 1
v_err_int = 0
previous_v_err = 0
integral_min = -5000
integral_max = 5000
pid_gains = {
    "0-1": {"kp": 500, "ki": 300, "kd": 20},
    "1-2": {"kp": 1000, "ki": 400, "kd": 15},
    "2-3": {"kp": 500, "ki": 100, "kd": 10},
    "3-4": {"kp": 200, "ki": 50, "kd": 5}
}

# Initialization
def initialize():
    global pwm, va_pin, vb_pin, ina_i2c
    va_pin = ADC(Pin(28))
    vb_pin = ADC(Pin(26))
    ina_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=2400000)

    pwm = PWM(Pin(9))
    pwm.freq(100000)

    # Start with no energy stored (9000)
    pwm.duty_u16(MIN_PWM)

# Control Functions
def saturate(signal, upper, lower):
    return max(min(signal, upper), lower)

# Timer Function
def tick(t):
    global timer_elapsed
    timer_elapsed = 1

# INA219 Class
class INA219:
    def __init__(self, address):
        self.address = address

    def read_register(self, register, length):
        return int.from_bytes(ina_i2c.readfrom_mem(self.address, register, length), 'big')

    def vshunt(self):
        reg_value = self.read_register(0x01, 2)
        return (float(reg_value) * 1e-5) * (-1 if reg_value > 2**15 else 1)

    def vbus(self):
        reg_value = self.read_register(0x02, 2) >> 3
        return float(reg_value) * 0.004

    def configure(self):
        ina_i2c.writeto_mem(self.address, 0x00, b'\x19\x9F')
        ina_i2c.writeto_mem(self.address, 0x05, b'\x00\x00')

# Utility Functions
def wait_for_stability():
    stable = False
    samples = []
    for _ in range(STABILITY_SAMPLES):
        current_va = va_pin.read_u16() / 65536 * 3.3
        samples.append(current_va)
        utime.sleep_ms(STABILITY_WAIT_TIME // STABILITY_SAMPLES)
    avg_va = sum(samples) / len(samples)
    max_diff = max(abs(v - avg_va) for v in samples)
    if max_diff < STABILITY_THRESHOLD:
        stable = True
    return stable

def get_desired_power():
    while True:
        try:
            P_desired = float(input("Enter the desired power output in Watts: "))
            if abs(P_desired) <= 4:
                return P_desired
            else:
                print("Power output must be within +-2 Watts of the desired value.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def calculate_soc(energy_stored):
    return min(100, max(0, (energy_stored - 6.4) / (MAX_CAPACITY - 6.4) * 100))

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

# Main Loop
def main():
    global timer_elapsed, count, first_run, v_err_int, previous_v_err

    initialize()

    while True:
        if first_run:
            ina = INA219(64)
            ina.configure()
            first_run = 0
            loop_timer = Timer(mode=Timer.PERIODIC, freq=1000, callback=tick)

        if timer_elapsed == 1:
            timer_elapsed = 0

            va = 1.017 * (12490 / 2490) * 3.3 * (va_pin.read_u16() / 65536)
            vb = 1.015 * (12490 / 2490) * 3.3 * (vb_pin.read_u16() / 65536)

            Vshunt = ina.vshunt()
            iL = -(Vshunt / SHUNT_OHMS)

            E_stored = round(0.5 * C * va**2 , 1)
            power_output = va * iL

            if (va >= 16.0 or E_stored >= MAX_CAPACITY or soc >= 100) and P_desired >= 0:
                P_desired = 0.005

            error = P_desired - power_output
            v_err_int += error
            v_err_int = saturate(v_err_int, integral_max, integral_min)
            v_err_deriv = error - previous_v_err

            pid_output = kp * error + ki * v_err_int + kd * v_err_deriv

            duty += int(pid_output)
            duty = saturate(duty, MAX_PWM, MIN_PWM)

            previous_v_err = error

            pwm.duty_u16(duty)

            utime.sleep_ms(5)

            soc = calculate_soc(E_stored)

            count = count + 1
            timer_elapsed = 0

            if count % (POWER_UPDATE_INTERVAL // 25) == 0:
                print(f"P: {power_output * 10:.2f} dW, SoC: {soc / 10:.3f}%, T: {count // 200} s")

            if count >= POWER_UPDATE_INTERVAL:
                average_power = power_sum / sample_count
                print(f"Average Power over last 5 seconds: {average_power:.2f} W")
                P_desired = get_desired_power()
                update_pid_gains(P_desired)
                power_sum = 0
                sample_count = 0
                count = 0

# Start the main loop
if __name__ == "__main__":
    main()
