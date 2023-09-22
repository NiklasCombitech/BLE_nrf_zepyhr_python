from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak.backends.characteristic import BleakGATTCharacteristic
import asyncio
from PairingAgentCallbacks import AgentCallbacks
import pydbus # better then pybluez/bleak?
import sys

target_name = "Nordic_LBS"
target_address = None

SERVICE_UUID    = "00001523-1212-efde-1523-785feabcd123"
BUTTON_UUID     = "00001524-1212-efde-1523-785feabcd123"
LED_UUID        = "00001525-1212-efde-1523-785feabcd123"

# getting connected bluetooth devices
bus = pydbus.SystemBus()
adapter = bus.get('org.bluez', '/org/bluez/hci0')
mngr = bus.get('org.bluez', '/')

def compare_device(deviceName: str):
    return deviceName == target_name

def device_filter(device: BLEDevice, adv: AdvertisementData): #filter devices, true = valid device, false = invalid device
    return compare_device(device.name)
    
def handle_disconnect(_: BleakClient):
    print("Device was disconnected, goodbye.")
    # cancelling all tasks effectively ends the program
    for task in asyncio.all_tasks():
        task.cancel()

def get_connected_devices():
    
    mngd_objs = mngr.GetManagedObjects()
    devices = []
    for path in mngd_objs:
        con_state = mngd_objs[path].get('org.bluez.Device1', {}).get('Connected', False)
        if con_state:
            addr = mngd_objs[path].get('org.bluez.Device1', {}).get('Address')
            name = mngd_objs[path].get('org.bluez.Device1', {}).get('Name')
            paired = mngd_objs[path].get('org.bluez.Device1', {}).get('Paired')
            uuids = mngd_objs[path].get('org.bluez.Device1', {}).get('UUIDs')

            devices.append({"addr":addr,"name":name,"paired":paired,"uuids":uuids})
    return devices


def buttonListener(_: BleakGATTCharacteristic, data: bytearray):
    print("button data: ", data)

async def main_pros():

    con_devs = get_connected_devices()
    for dev in con_devs:
        if compare_device(dev['name']):
            print("Device already connected, please manually disconnect the bluetooth device ''" + dev['name'] + "'' and restart.")
            return
    
    device = await BleakScanner.find_device_by_filter(device_filter)
    
    if device is None:
        print("device was not found")
        return
    else:
        print("Device Found: " + str(device))
        print("--------------------------")
    
    try:
        device = await BleakScanner.find_device_by_filter(device_filter)
    except Exception:
        print("device was not paired")
              
    async with BleakClient(device) as client, AgentCallbacks() as callbacks:
        try:
            await client.pair(callbacks)

            global exit_client
            exit_client = client

            print("pairing complete.")
            # Devices paired what now?
            await client.start_notify(BUTTON_UUID,buttonListener) # listen to button stuffs

            service = client.services.get_service(SERVICE_UUID)
            led = service.get_characteristic(LED_UUID)
            loop = asyncio.get_running_loop()

            print("subscribed to characteristic.")
            while True:
                data = await loop.run_in_executor(None, sys.stdin.buffer.readline)

                if str(data).__contains__("--exit"):
                    print("exiting...")
                    await client.disconnect()
                    print("Disconnected!")
                    for task in asyncio.all_tasks():
                        task.cancel()


        except Exception:
            print("paring failed or cancled.")

if __name__ == "__main__":
    try:
        asyncio.run(main_pros())
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass