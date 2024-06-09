from machine import I2C, Pin

class INA219:
    REG_CONFIG = 0x00
    REG_SHUNTVOLTAGE = 0x01
    REG_BUSVOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05
    
    def __init__(self, shunt_ohms, address, maxi):
        self.address = address
        self.shunt_ohms = shunt_ohms
        self.i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=2400000)
        self.configure()
    
    def vshunt(self):
        reg_bytes = self.i2c.readfrom_mem(self.address, self.REG_SHUNTVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big')
        if reg_value > 2**15: #negative
            sign = -1
            for i in range(16): 
                reg_value = (reg_value ^ (1 << i))
        else:
            sign = 1
        return float(reg_value) * 1e-5 * sign
    
    def vbus(self):
        reg_bytes = self.i2c.readfrom_mem(self.address, self.REG_BUSVOLTAGE, 2)
        reg_value = int.from_bytes(reg_bytes, 'big') >> 3
        return float(reg_value) * 0.004
    
    def configure(self):
        self.i2c.writeto_mem(self.address, self.REG_CONFIG, b'\x19\x9F')
        self.i2c.writeto_mem(self.address, self.REG_CALIBRATION, b'\x00\x00')

