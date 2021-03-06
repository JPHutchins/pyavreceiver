"""pyavreceiver - interface to control Audio/Video Receivers."""
import asyncio
import logging

import aiohttp

from pyavreceiver import const
from pyavreceiver.denon.http_api import DenonAVRApi, DenonAVRX2016Api, DenonAVRXApi
from pyavreceiver.denon.receiver import DenonReceiver
from pyavreceiver.error import AVReceiverIncompatibleDeviceError

_LOGGER = logging.getLogger(__name__)


async def factory(host: str, log_level: int = logging.WARNING):
    """Return an instance of an AV Receiver."""
    _LOGGER.setLevel(log_level)
    names, tasks = [], []
    async with aiohttp.ClientSession() as session:
        for name, url in const.UPNP_ENDPOINTS.items():
            names.append(name)
            tasks.append(
                asyncio.create_task(session.get(f"http://{host}{url}", timeout=5))
            )
        responses = await asyncio.gather(*tasks)
        for name, response in zip(names, responses):
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
