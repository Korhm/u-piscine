from wifi import wlan_connect
from microdot_asyncio import Microdot, abort
from microdot_cors import CORS
import gc
import uasyncio as asyncio
from micropython import const
from functools import wraps
from config import config
from pool_heater import PoolHeater

PIN_SENSORS = const(26)
PIN_PUMP = const(21)
HTTP_PORT = const(80)

asyncio.create_task(wlan_connect())
chauffage = PoolHeater(pin_sensors=PIN_SENSORS, pin_pump=PIN_PUMP)

app = Microdot()
CORS(app=app, allowed_origins="*", allow_credentials=True)

def validate_token(func):
  @wraps(func)
  def decorated_function(*args, **kwargs):
    request = args[0]
    try:
        token = request.headers['Authorization'].replace('Bearer ', '')
        if not token in config.get('authorized_tokens'):
            raise
    except:
        abort(401)
    return func(*args, **kwargs)
  return decorated_function

@app.get('/piscine')
def index(request):
    return "piscine micropython"

@app.get('/piscine/power')
@validate_token
async def get_power(request):
    try:
        return {"result": "ok", "data": chauffage.get_power_value() }
    except Exception as ex:
        print(ex)
        abort(500, {"result": "err", "status": 500, "err": type(ex).__name__ })

@app.put('/piscine/power')
@validate_token
async def put_power(request):
    power = request.args.get('power')

    if power == 'on':
        chauffage.start()
    elif power == 'off':
        chauffage.stop()
    else:
        abort(400, {"result": "err", "status": 400, "err": "Invalid value for 'power'. Allowed values are 'on', 'off'"})

    try:
        return {"result": "ok", "data": chauffage.get_power_value() }
    except Exception as ex:
        print(ex)
        abort(500, {"result": "err", "status": 500, "err": type(ex).__name__ })

@app.get('/piscine/temperatures')
@validate_token
async def get_temperatures(request):
    try:
        return {"result": "ok", "data": chauffage.get_temperatures() }
    except Exception as ex:
        print(ex)
        abort(500, {"result": "err", "status": 500, "err": type(ex).__name__ })

@app.get('/piscine/sensors')
@validate_token
async def get_sensors(request):
    try:
        return {"result": "ok", "data": chauffage.get_sensors() }
    except Exception as ex:
        print(ex)
        abort(500, {"result": "err", "status": 500, "err": type(ex).__name__ })

@app.get('/piscine/sensors/scan')
@validate_token
async def scan_sensors(request):
    try:
        return {"result": "ok", "data": chauffage.scan_sensors() }
    except Exception as ex:
        print(ex)
        abort(500, {"result": "err", "status": 500, "err": type(ex).__name__ })

gc.collect()

app.run(port=HTTP_PORT, debug=True)