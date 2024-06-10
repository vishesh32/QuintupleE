import utime

def saturate(signal, upper, lower): 
    return max(min(signal, upper), lower)

def get_desired_power():
    while True:
        try:
            P_desired = float(input("Enter the desired power output in Watts: "))
            if abs(P_desired) <= 3:  # Limiting the absolute value of input to <= 4
                return P_desired
            else:
                print("Power output must be within +-3 Watts of the desired value.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def calculate_soc(energy_stored, max_capacity):
    return min(100, max(0, (energy_stored - 4.8) / (max_capacity - 4.8) * 100))

def update_pid_gains(P_desired, pid_gains):
    if 0 <= abs(P_desired) <= 1:
        gains = pid_gains["0-1"]
    elif 1 < abs(P_desired) <= 2:
        gains = pid_gains["1-2"]
    elif 2 < abs(P_desired) <= 3:
        gains = pid_gains["2-3"]
    else:
        gains = pid_gains["0-1"]
    return gains["kp"], gains["ki"], gains["kd"]
