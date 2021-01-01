"""pyavreceiver - interface to control Audio/Video Receivers."""
import asyncio

import aiohttp

from pyavreceiver import const
from pyavreceiver.denon.http_connection import (
    DenonAVRApi,
    DenonAVRX2016Api,
    DenonAVRXApi,
)
from pyavreceiver.denon.receiver import DenonReceiver
from pyavreceiver.error import AVReceiverIncompatibleDeviceError


async def factory(host: str):
    """Return an instance of an AV Receiver."""
    async with aiohttp.ClientSession() as session:
        names, tasks = [], []
        for name, url in const.UPNP_ENDPOINTS.items():
            names.append(name)
            tasks.append(
                asyncio.create_task(session.get(f"http://{host}{url}", timeout=5))
            )
    for name, response in zip(names, await asyncio.gather(*tasks)):
        if response.status == 200:
            if name == "denon-avr-x-2016":
                http_api = DenonAVRX2016Api(host, await response.text())
                return DenonReceiver(host, http_api=http_api)
            if name == "denon-avr-x":
                http_api = DenonAVRXApi(host, await response.text())
                return DenonReceiver(host, http_api=http_api)
            if name == "denon-avr":
                http_api = DenonAVRApi(host, await response.text())
                return DenonReceiver(host, http_api=http_api)
    raise AVReceiverIncompatibleDeviceError
