class PIDController:
    def __init__(self, kp, ki, kd, integral_min, integral_max):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral_min = integral_min
        self.integral_max = integral_max
        self.previous_error = 0
        self.integral = 0

    def update(self, error):
        self.integral += error
        self.integral = max(min(self.integral, self.integral_max), self.integral_min)
        derivative = error - self.previous_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error
        return output

