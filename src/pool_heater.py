try:
    from machine import Pin # type: ignore
except:
    from tests.fakes.machine import Pin

try:
    import onewire # type: ignore
except:
    import tests.fakes.onewire as onewire

try:
    import ds18x20 # type: ignore
except:
    import tests.fakes.ds18x20 as ds18x20

from src.temp_sensors import temp_sensors_addr
from os import listdir
import time

class TempSensor:
    def __init__(self, name, addr, rom):
        self.name = name
        self.addr = addr
        self.rom = rom

    def __repr__(self):
        return 'TempSensor: {} ({})'.format(self.name, self.addr)

    def to_json(self):
        return ({
            "name": self.name,
            "addr": self.addr
        })

    @staticmethod
    def get_addr(_bytes):
        return ' '.join(['0x{:02x}'.format(_bytes[i]) for i in range(0, 8)])

class PoolHeater:
    ON = "on"
    OFF = "off"
    
    def __init__(self, **kwargs) -> None:
        """
        pin_sensors
        pin_pump
        """
        self._pin_sensors = Pin(kwargs.get('pin_sensors', 0), Pin.IN)
        self._pin_pump = Pin(kwargs.get('pin_pump', 1), Pin.OUT)

        self._ds18x20 = ds18x20.DS18X20(onewire.OneWire(self._pin_sensors))
        

        self.scanned_sensors = dict()
        self.scan_sensors()
        
        self.power = PoolHeater.OFF

        self.restore_state()

    def scan_sensors(self):
        print('Scanning DS18x20 sensors ...')
        self.roms = self._ds18x20.scan()

        for rom in self.roms:
            addr = TempSensor.get_addr(rom)
            name = temp_sensors_addr.get(addr)
            if name:
                self.scanned_sensors[name] = TempSensor(name, addr, rom)
                print("DS18x20 sensors found: ", self.scanned_sensors[name])
            else:
                print("Unknown DS18x20 sensors: ", addr) 

        print('Number of DS18x20 sensors found: {}'.format(len(self.scanned_sensors)))
        
        return len(self.scanned_sensors)

    def get_sensors(self):
        return [s.to_json() for s in self.scanned_sensors.values()]


    def start(self):
        self._pin_pump.value(1)
        self.power = PoolHeater.ON
        self.save_state("power")

    def stop(self):
        self._pin_pump.value(0)
        self.power = PoolHeater.OFF
        self.save_state("power")

    def get_power_value(self):
        return self.power

    def get_temperatures(self):
        data = dict()
        
        self._ds18x20.convert_temp()
        time.sleep_ms(800)
        for addr, name in temp_sensors_addr.items():
            if name in self.scanned_sensors:
                data[name] = self._ds18x20.read_temp(self.scanned_sensors[name].rom)
            else:
                data[name] = None
        data["timestamp"] = time.time()
        return data

    def restore_state(self):
        print("Restoring state ...")
        
        for file in listdir():
            if file.endswith(".state"):
                with open(file) as f:
                    value = f.read().rstrip()
                    if file == "power.state":
                        print(" ... {} -> {}".format(file, value))
                        self.power = value
                        getattr(self._pin_pump, value)()
    
    def save_state(self, name):
        print("save state...")
        with open(name + ".state", "w") as f:
            f.write(str(getattr(self, name)))