#
# Pairing agent by https://github.com/bojanpotocnik
#
import asyncio
import sys
from bleak import BaseBleakAgentCallbacks
from bleak.backends.device import BLEDevice

class AgentCallbacks(BaseBleakAgentCallbacks):
    def __init__(self) -> None:
        super().__init__()
        self._reader = asyncio.StreamReader()

    async def __aenter__(self):
        loop = asyncio.get_running_loop()
        protocol = asyncio.StreamReaderProtocol(self._reader)
        self._input_transport, _ = await loop.connect_read_pipe(
            lambda: protocol, sys.stdin
        )
        return self

    async def __aexit__(self, *args):
        self._input_transport.close()

    async def _input(self, msg: str) -> str:
        """
        Async version of the builtin input function.
        """
        print(msg, end=" ", flush=True)
        return (await self._reader.readline()).decode().strip()

    async def confirm(self, device: BLEDevice) -> bool:
        print(f"{device.name} wants to pair.")
        response = await self._input("confirm (y/n)?")

        return response.lower().startswith("y")

    async def confirm_pin(self, device: BLEDevice, pin: str) -> bool:
        print(f"{device.name} wants to pair.")
        response = await self._input(f"does {pin} match (y/n)?")

        return response.lower().startswith("y")

    async def display_pin(self, device: BLEDevice, pin: str) -> None:
        print(f"{device.name} wants to pair.")
        print(f"enter this pin on the device: {pin}")
        # wait for cancellation
        await asyncio.Event().wait()

    async def request_pin(self, device: BLEDevice) -> str:
        print(f"{device.name} wants to pair.")
        response = await self._input("enter pin:")

        return response