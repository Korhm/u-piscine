
## Build micropython
To optimize memory usage, buid a micropython firmware with pre-compiled pacakges

https://docs.micropython.org/en/latest/reference/manifest.html#

### Raspberry Pi Pico W

```bash
sudo apt-get install build-essential cmake gcc-arm-none-eabi libnewlib-arm-none-eabi libstdc++-arm-none-eabi-newlib
cd /home/damien/dev/micropython
git pull

cd /home/damien/dev/micropython
git pull
git submodule update --init
cd lib/pico-sdk
git submodule update --init
cd ../../ports/rp2

make FROZEN_MANIFEST=/home/damien/dev/upiscine/boards/manifest-rp2-PICO_W.py BOARD=PICO_W submodules
make FROZEN_MANIFEST=/home/damien/dev/upiscine/boards/manifest-rp2-PICO_W.py BOARD=PICO_W clean
make FROZEN_MANIFEST=/home/damien/dev/upiscine/boards/manifest-rp2-PICO_W.py BOARD=PICO_W
```

Upload the file `/home/damien/dev/micropython/ports/rp2/build-PICO_W/firmware.uf2` into the RP2 device in Bootsel mode (https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico/3)
