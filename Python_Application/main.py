from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak.backends.characteristic import BleakGATTCharacteristic
import asyncio


target_name = "Nordic_UART_Service"
target_address = None

def device_filter(device: BLEDevice, adv: AdvertisementData): #filter devices, true = valid device, false = invalid device
    if device.name == target_name:
        return True
    return False

    
def handle_disconnect(_: BleakClient):
    print("Device was disconnected, goodbye.")
    # cancelling all tasks effectively ends the program
    for task in asyncio.all_tasks():
        task.cancel()

async def main_pros():
    device = await BleakScanner.find_device_by_filter(device_filter)

    print("Device Found: " + str(device))
    print("--------------------------")
    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:
        print(1)
        await client.connect()
        print(2)
        

if __name__ == "__main__":
    try:
        asyncio.run(main_pros())
    except asyncio.CancelledError:
        # task is cancelled on disconnect, so we ignore this error
        pass