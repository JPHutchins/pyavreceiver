"""Define an HTTP connection to a Denon/Marantz receiver."""
from xml.etree import ElementTree as ET

import aiohttp

from pyavreceiver import const
from pyavreceiver.denon import const as denon_const
from pyavreceiver.http_connection import HTTPConnection


class DenonHTTPApi(HTTPConnection):
    """Define the Denon HTTP API."""

    async def get_device_info(self) -> dict:
        "Get information about the device"
        xml = await self._get_device_info()
        return DenonHTTPApi.make_device_info_dict(xml)

    async def get_source_names(self) -> dict:
        """Get the renamed sources."""
        xml = await self.get_renamed_deleted_sources()
        return DenonHTTPApi.make_renamed_dict(xml)

    async def _get_device_info(self):
        """Get information about the device."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{self.host}:{self.port}{self._device_info_url}"
            ) as resp:
                text = await resp.text()
                return text

    async def _app_command(self, xml: bytes):
        """Make request to AppCommand.xml endpoint."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{self.host}:{self.port}/goform/AppCommand.xml", data=xml
            ) as resp:
                text = await resp.text()
                return text

    async def get_renamed_deleted_sources(self):
        """Get the renamed and deleted sources."""
        xml = DenonHTTPApi.make_xml_request(["GetRenameSource", "GetDeletedSource"])
        resp = await self._app_command(xml)
        return resp

    @staticmethod
    def make_renamed_dict(xml) -> dict:
        """Parse the XML response for renamed and deleted sources."""
        root = ET.fromstring(xml)
        deleted = set()
        deleted_root = root.find("*/functiondelete")
        for entry in deleted_root.findall("list"):
            try:
                if entry.find("use").text == "0":
                    deleted.add(entry.find("name").text.strip().lower())
            except AttributeError:
                continue
        rename_map = {}
        renamed_root = root.find("*/functionrename")
        for entry in renamed_root.findall("list"):
            try:
                name = entry.find("name").text.strip().lower()
                rename = entry.find("rename").text.strip()
            except AttributeError:
                continue
            if name not in deleted:
                rename_map[rename] = (
                    denon_const.MAP_HTTP_SOURCE_NAME_TO_TELNET.get(name) or name.upper()
                )
        return rename_map

    @staticmethod
    def make_device_info_dict(xml) -> dict:
        """Parse response for information."""
        root = ET.fromstring(xml)
        info = {
            const.INFO_MODEL: get_text(root, "ModelName"),
            const.INFO_MAC: get_text(root, "MacAddress"),
            const.INFO_ZONES: get_text(root, "DeviceZones") or "0",
        }

        return info

    @staticmethod
    def make_xml_request(commands: list) -> bytes:
        """Prepare XML body for Denon API."""
        xml_parts = ['<?xml version="1.0" encoding="utf-8"?>\n', "<tx>"]
        cmd_l = '<cmd id="1">'
        cmd_r = "</cmd>"
        for i, command in enumerate(commands):
            if i != 0 and i % 5 == 0:
                # API allows multiple XML roots, limit 5 commands each
                xml_parts.append("</tx><tx>")
            xml_parts.append(f"{cmd_l}{command}{cmd_r}")
        xml_parts.append("</tx>")
        return "".join(xml_parts).encode()


class DenonAVRX2016Api(DenonHTTPApi):
    """Define the Denon/Marantz AVR-X 2016 API."""

    def __init__(self, host, upnp_data, session=None):
        super().__init__(host, session)
        self.port = denon_const.API_2016_PORT
        self._device_info_url = denon_const.API_2016_DEVICE_INFO_URL


def get_text(root: ET.Element, tag: str):
    """Get the text attribute if it exists."""
    elem = root.find(tag)
    if elem is not None:
        return elem.text
    return None
