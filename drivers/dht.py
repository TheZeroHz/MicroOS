class DHTSensor:
    def __init__(self, pin):
        self.pin = pin

    def read(self):
        return {"temp_c": None, "humidity": None}
