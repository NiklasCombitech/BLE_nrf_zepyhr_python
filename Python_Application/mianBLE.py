import asyncio
from bleak import BleakScanner
from bleak import BleakClient
from bleak.backends.bluezdbus.agent import BluetoothAgent

async def main():
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == "Nordic_LBS" :

            agent = BluetoothAgent
            agent.start(BluetoothAgent)
            #Insert your code to get a device through scan, filter,etc
            client = BleakClient(d) #assumes you already have a device
            await client.connect()
            agent.set_passkey(input("passkey: "))
            
            await client.pair()
            print(d)
            async with BleakClient(d.address) as client:
                await client.connect()
                s = await client.get_services()
                print(s)
                await client.disconnect()

asyncio.run(main())