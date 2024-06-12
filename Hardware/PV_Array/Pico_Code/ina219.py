from machine import I2C

class INA219:
    # Register Locations
    REG_CONFIG = 0x00
    REG_SHUNTVOLTAGE = 0x01
    REG_BUSVOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05

    def __init__(self, i2c: I2C, shunt_resistance: float, address: int):
        self.i2c = i2c
        self.shunt = shunt_resistance
        self.address = address

    def vshunt(self) -> float:
        reg_bytes = self.i2c.readfrom_mem(self.address, self.REG_SHUNTVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big')
        if reg_value > 2 ** 15:
            reg_value -= 2 ** 16
        return float(reg_value) * 1e-5

    def vbus(self) -> float:
        reg_bytes = self.i2c.readfrom_mem(self.address, self.REG_BUSVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big') >> 3
        return float(reg_value) * 0.004

    def configure(self):
        self.i2c.writeto_mem(self.address, self.REG_CONFIG, b'\x19\x9F')
        self.i2c.writeto_mem(self.address, self.REG_CALIBRATION, b'\x00\x00')

