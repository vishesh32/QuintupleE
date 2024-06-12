from machine import Pin, ADC, PWM, Timer, I2C
import utime
from ina219 import INA219
from pid import PIDController
from utils import saturate, get_irradiance

def irradiance_simulation():
    vb_pin = ADC(Pin(26))
    ina_i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=2400000)
    pwm = PWM(Pin(9))
    pwm.freq(100000)
    min_pwm = 1000
    max_pwm = 64536
    pwm_out = min_pwm

    SHUNT_OHMS = 0.10
    MPP = 4

    irradiance = 100
    power_sum = 0
    sample_count = 0
    P_desired = MPP

    global timer_elapsed
    timer_elapsed = 0
    count = 0
    first_run = 1

    kp = 1000
    ki = 5
    kd = 0

    v_err_int = 0
    previous_v_err = 0
    integral_min = -5000
    integral_max = 5000

    stability_threshold = 0.005
    stability_samples = 10
    stability_wait_time = 150

    def tick(t):
        global timer_elapsed
        timer_elapsed = 1

    pid = PIDController(kp, ki, kd, integral_min, integral_max)

    def update_pid(error):
        nonlocal v_err_int, previous_v_err
        v_err_int += error
        v_err_int = saturate(v_err_int, integral_max, integral_min)
        pid_output = pid.update(error)
        previous_v_err = error
        return pid_output

    duty = int(min_pwm)
    duty = saturate(duty, max_pwm, min_pwm)
    pwm.duty_u16(duty)

    while True:
        if first_run:
            ina = INA219(ina_i2c, SHUNT_OHMS, 64)
            ina.configure()
            first_run = 0
            loop_timer = Timer(mode=Timer.PERIODIC, freq=1000, callback=tick)

        if timer_elapsed == 1:
            timer_elapsed = 0

            vb = 1.015 * (12490 / 2490) * 3.3 * (vb_pin.read_u16() / 65536)
            Vshunt = ina.vshunt()
            iL = Vshunt / SHUNT_OHMS
            power_output = vb * iL

            error = P_desired - power_output
            pid_output = update_pid(error)

            pwm_out += int(pid_output)
            pwm_out = saturate(pwm_out, max_pwm, min_pwm)
            duty = int(65536 - pwm_out)
            pwm.duty_u16(duty)

            utime.sleep_ms(5)
            power_sum += power_output
            sample_count += 1
            count += 1

            if count % 25 == 0:
                print(f"P: {power_output:.2f} W")

            if count % 1000 == 0:
                print("5 seconds mark")

            if count >= 2000:
                average_power = power_sum / sample_count
                print(f"Average Power over last 5 seconds: {average_power:.2f} W")
                power_sum = 0
                sample_count = 0
                count = 0

