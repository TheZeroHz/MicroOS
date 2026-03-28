from hal.display import DisplayHAL
from hal.gpio import GPIOHAL
from hal.i2c import I2CHAL
from hal.spi import SPIHAL
from hal.uart import UARTHAL
from hal.adc import ADCHAL
from hal.pwm import PWMHAL
from hal.touch import TouchHAL


class HAL:
    def __init__(self, config=None, logger=None):
        self.config = config or {}
        self.logger = logger
        self.display = DisplayHAL(self.config, logger=logger)
        self.gpio = GPIOHAL(self.config, logger=logger)
        self.i2c = I2CHAL(self.config, logger=logger)
        self.spi = SPIHAL(self.config, logger=logger)
        self.uart = UARTHAL(self.config, logger=logger)
        self.adc = ADCHAL(self.config, logger=logger)
        self.pwm = PWMHAL(self.config, logger=logger)
        self.touch = TouchHAL(self.config, logger=logger)

    def init_all(self):
        if self.logger:
            self.logger.info("HAL ready")
