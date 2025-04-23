import asyncio
from uasyncio import StreamWriter, StreamReader
from machine import UART, Pin


class SET_CMD:
    server_tcp = b'\x57\xab\x10\x00'
    save = b'\x57\xab\x0d'  
    exec_conf = b'\x57\xab\x0e'
    leave = b'\x57\xab\x5e'

    @staticmethod
    def local_ip(ip):
        return b'\x57\xab\x11' + bytes(bytearray(ip))

    @staticmethod
    def subset_mask(ip):
        return b'\x57\xab\x12' + bytes(bytearray(ip))

    @staticmethod
    def gateway(ip):
        return b'\x57\xab\x13' + bytes(bytearray(ip))

    @staticmethod
    def port_1(port):
        return b'\x57\xab\x14' + port.to_bytes(2, 'little')

    @staticmethod
    def baud_rate_1(baud_rate=9600):
        return b'\x57\xab\x21' + baud_rate.to_bytes(4, 'little')

    @staticmethod
    def domaine_name(name):
        return b'\x57\xab\x34' + name.encode("utf-8")
    
    @staticmethod
    def dhcp_enable(enable=True):
        return b'\x57\xab\x33' + (b'\x01' if enable else b'\x00')

class GET_CMD:
    local_ip = b'\x57\xab\x61'
    subset_mask = b'\x57\xab\x62'
    gateway = b'\x57\xab\x63'
    port_1 = b'\x57\xab\x64'

class CH9121:
    """Server using CH9121 chipset"""

    def __init__(self):
        self.uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
        self.cfg = Pin(14, Pin.OUT, Pin.PULL_UP)
        self.rst = Pin(17, Pin.OUT, Pin.PULL_UP)
        self.writer = StreamWriter(self.uart0, {})
        self.reader = StreamReader(self.uart0)
        self.rst.value(1)


    async def set_tcp_server(self, ip, port, gateway, mask):
        commands = [
            SET_CMD.server_tcp,
            SET_CMD.local_ip(ip),
            SET_CMD.port_1(port),
            SET_CMD.subset_mask(mask),
            SET_CMD.gateway(gateway),
            SET_CMD.baud_rate_1(),
        ]
        return await self.set_config(commands)
    
    async def set_tcp_server_dhcp(self, port=80):
        # The IP address is stored in the EEPROM of CH9121
        # Reset it only if no IP yet configured or the GW is not reachable
        

        commands = [
            GET_CMD.local_ip,
            GET_CMD.gateway,
        ]
        x = await self.read_config(commands)
        ch9121localip = f"{x[0]}.{x[1]}.{x[2]}.{x[3]}"
        ch9121gateway = f"{x[4]}.{x[5]}.{x[6]}.{x[7]}"

        if (ch9121localip == b'\x00\x00\x00\x00' or ch9121localip == b'' or ch9121localip == b'0.0.0.0' or ch9121localip == '0.0.0.0' or ch9121localip is None):
            await asyncio.sleep(0.5)
            print("Current IP is not set, using DHCP")
            commands = [
                SET_CMD.server_tcp,
                SET_CMD.dhcp_enable(True),
                SET_CMD.port_1(port),
                SET_CMD.baud_rate_1(),
            ]
        else:
            print(f"Current IP is set ({ch9121localip}), Let CH9131 keep it")
            commands = [
                SET_CMD.server_tcp,
                SET_CMD.port_1(port),
                SET_CMD.baud_rate_1(),
            ]
        await self.set_config(commands)

        await asyncio.sleep(0.5)
        commands = [
            GET_CMD.local_ip,
            GET_CMD.subset_mask,
            GET_CMD.gateway,
        ]
        x = await self.read_config(commands)
        ch9121localip = f"{x[0]}.{x[1]}.{x[2]}.{x[3]}"
        ch9121subnet = f"{x[4]}.{x[5]}.{x[6]}.{x[7]}"
        ch9121gateway = f"{x[8]}.{x[9]}.{x[10]}.{x[11]}"

        print('network config:', (ch9121localip, ch9121subnet, ch9121gateway))        

    async def set_config(self, commands):
        commands.append(SET_CMD.save)
        commands.append(SET_CMD.exec_conf)
        commands.append(SET_CMD.leave)
        try:
            self.cfg.value(0)
            await asyncio.sleep_ms(100)
            for cmd in commands:
                await self.writer.awrite(cmd)
                await asyncio.sleep(0.1)
            n = self.uart0.any()
            await self.reader.read(n)                
        except Exception as ex:
            print(ex)
        finally:
            self.cfg.value(1)

    async def read_config(self, commands):
        data = None
        try:
            self.cfg.value(0)
            for cmd in commands:
                await self.writer.awrite(cmd)
                await asyncio.sleep(.1)
            n = self.uart0.any()
            data = await self.reader.read(n)
        except Exception as ex:
            print(ex)
        finally:
            self.cfg.value(1)
            return data
        
    async def ifconfig(self, ip, mask, gateway):
        commands = [
            SET_CMD.local_ip(ip),
            SET_CMD.subset_mask(mask),
            SET_CMD.gateway(gateway),
        ]
        return await self.set_config(commands)
