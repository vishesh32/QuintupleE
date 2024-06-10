from helper_functions import saturate

class PIDController:
    def __init__(self, kp, ki, kd, integral_min, integral_max):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_min = integral_min
        self.integral_max = integral_max
        self.v_err_int = 0
        self.previous_v_err = 0
    
    def update(self, error):
        self.v_err_int += error  # Integrate the error
        self.v_err_int = saturate(self.v_err_int, self.integral_max, self.integral_min)  # Clamp the integral term
        v_err_deriv = error - self.previous_v_err  # Calculate the derivative of the error
        
        # Calculate the PID output
        pid_output = self.kp * error + self.ki * self.v_err_int + self.kd * v_err_deriv
        
        # Update the previous error
        self.previous_v_err = error
        
        return pid_output
