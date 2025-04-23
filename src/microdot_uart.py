from microdot import Microdot
from machine import UART, Pin
import asyncio

class StreamReaderUART:
    def __init__(self, uart):
        self.uart = uart

    async def readline(self):
        line = b""
        while True:
            if self.uart.any():
                char = self.uart.read(1)
                if char == b'\n':
                    break
                if char not in (b'\x00', b''):
                    line += char
            await asyncio.sleep(0)
        return line
    
    async def readexactly(self, n):
        print(f"readexactly {n} {self.uart.any()}")
        try:
            data = b""
            for _ in range(n):
                data += self.uart.read(1)
                await asyncio.sleep(0)
            return data
        except Exception as e:
            print(e)
            return b""

class StreamWriterUART:
    def __init__(self, uart):
        self.uart = uart

    async def awrite(self, data):
        await asyncio.sleep(0)  # Laisse tourner l'event loop
        self.uart.write(data)
        await asyncio.sleep(0.01 * len(data))


    async def aclose(self):
        await asyncio.sleep(0.05) # Implicit flush

    def get_extra_info(self, info):
        return {
            "peername": "127.0.0.1"
        }.get(info, None)

class MicrodotUART(Microdot):
    RST = Pin(17, Pin.OUT, Pin.PULL_UP) #CH9121 external reset input pin, low active
    CFG = Pin(14, Pin.OUT, Pin.PULL_UP) #CH9121 configuration pin, 0 to config, 1 to exit

    def __init__(self):
        super().__init__()

        self.RST.value(1) #CH9121 external reset input pin 17, (0 active, 1 inactive)
        self.CFG.value(1) #CH9121 configuration pin, 0 to config, 1 to exit

        self.uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

    async def start_server(self, reader, writer, debug=False):
        self.debug = debug

        if self.debug:  # pragma: no cover
            print('Starting async server on UART')

        while True:
            await self.handle_request(StreamReaderUART(reader), StreamWriterUART(writer))

    def run(self, debug=False):
        asyncio.run(self.start_server(self.uart, self.uart, debug=debug))  # pragma: no cover