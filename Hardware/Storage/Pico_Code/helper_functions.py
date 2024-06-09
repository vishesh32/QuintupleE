def saturate(signal, upper, lower): 
    return max(min(signal, upper), lower)

def get_desired_power():
    while True:
        try:
            P_desired = float(input("Enter the desired power output in Watts: "))
            if abs(P_desired) <= 2:  # Limiting the absolute value of input to <= 4
                return P_desired
            else:
                print("Power output must be within +-2 Watts of the desired value.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def calculate_soc(energy_stored, MAX_CAPACITY):
    return min(100, max(0, (energy_stored - 6.4) / (MAX_CAPACITY - 6.4) * 100))

def update_pid_gains(P_desired, pid_gains):
    global kp, ki, kd
    if 0 <= abs(P_desired) < 1:
        gains = pid_gains["0-1"]
    elif 1 <= abs(P_desired) <= 2:
        gains = pid_gains["1-2"]
    else:
        gains = pid_gains["0-1"]
    kp, ki, kd = gains["kp"], gains["ki"], gains["kd"]
