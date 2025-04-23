class Pin:
    IN=0
    OUT=1

    def __init__(self, pin, way) -> None:
        self.pin = pin
        self.way = way
        self.val = None

    def value(self, val):
        self.val = val

    def on(self):
        self.val = 1

    def off(self):
        self.val = 0