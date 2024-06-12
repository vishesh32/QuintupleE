def saturate(signal, upper, lower):
    return max(min(signal, upper), lower)

def get_irradiance():
    while True:
        try:
            irradiance = float(input("Enter irradiance as %: "))
            if 0 <= irradiance <= 100:
                return irradiance
            else:
                print("Irradiance % is not valid")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

