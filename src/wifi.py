import network
import ntptime
from config import config
from time import sleep
from rp2 import country

status_map = {
    network.STAT_IDLE: ('STAT_IDLE', 'no connection and no activity'),
    network.STAT_CONNECTING: ('STAT_CONNECTING', 'connecting in progress'),
    network.STAT_WRONG_PASSWORD: ('STAT_WRONG_PASSWORD', 'failed due to incorrect password'),
    network.STAT_NO_AP_FOUND: ('STAT_NO_AP_FOUND', 'failed because no access point replied'),
    network.STAT_CONNECT_FAIL: ('STAT_CONNECT_FAIL', 'failed due to other problems'),
    network.STAT_GOT_IP: ('STAT_GOT_IP', 'connection successful')
}

async def wlan_connect():

    country('FR')

    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)

    wlan = network.WLAN(network.STA_IF)
    wlan.deinit()

    if not wlan.isconnected():
        print('Connecting to network {} ...'.format(config.get('wifi_sid')))
        wlan.active(True)
        
        ifconfig = config.get('wifi_ifconfig')
        if ifconfig:
            wlan.ifconfig(ifconfig)
        
        wlan.connect(config.get('wifi_sid'), config.get('wifi_password'))
        while not wlan.isconnected():
            print('Error: {} ({})'.format(status_map.get(wlan.status()), wlan.status()))
            sleep(1)
            
    ntptime.settime()
    print('network config:', wlan.ifconfig())