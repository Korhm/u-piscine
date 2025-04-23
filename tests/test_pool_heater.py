import unittest
from src.pool_heater import PoolHeater

class TestPoolHeater(unittest.TestCase):
    def test_start(self):
        ph = PoolHeater(pin_sensors=1, pin_pump=2)
        ph.start()

        self.assertEqual(ph.power, "on")

    def test_stop(self):
        ph = PoolHeater(pin_sensors=1, pin_pump=2)
        ph.stop()

        self.assertEqual(ph.power, "off")

if __name__ == '__main__':
    unittest.main()