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
        self.make_device_info_dict(xml)
        if self._upnp_data:
            self.make_device_info_dict(self._upnp_data)
        return self.device_info

    async def get_source_names(self) -> dict:
        """Get the renamed sources."""
        xml_body = DenonHTTPApi.make_xml_request(
            ["GetRenameSource", "GetDeletedSource"]
        )
        xml = await self._app_command(xml_body)
        if xml:
            return DenonHTTPApi.make_renamed_dict(xml)

        # AppCommand endpoint failed, use alternate
        xml = await self._get_mainzone_xml() or await self._get_status_xml()
        return DenonHTTPApi.make_renamed_dict_legacy(xml)

    async def _get_status_xml(self) -> str:
        """Get the Main Zone status XML endpoint."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{self.host}:{self.port}{denon_const.API_MAIN_ZONE_XML_STATUS_URL}"
            ) as resp:
                if resp.status == 200:
                    return await resp.text()

    async def _get_mainzone_xml(self) -> str:
        """Get the Main Zone status XML endpoint."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{self.host}:{self.port}{denon_const.API_MAIN_ZONE_XML_URL}"
            ) as resp:
                if resp.status == 200:
                    return await resp.text()

    async def _get_device_info(self):
        """Get information about the device."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{self.host}:{self.port}{self._device_info_url}"
            ) as resp:
                if resp.status == 200:
                    return await resp.text()

    async def _app_command(self, xml: bytes):
        """Make request to AppCommand.xml endpoint."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{self.host}:{self.port}/goform/AppCommand.xml", data=xml
            ) as resp:
                if resp.status == 200:
                    return await resp.text()
                return False

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
    def make_renamed_dict_legacy(xml) -> dict:
        """Parse the XML response for renamed and deleted sources."""
        root = ET.fromstring(xml)

        original_names = []
        skip_source = 0
        for name in root.find("InputFuncList"):
            try:
                if name.text == "SOURCE":
                    skip_source = 1  # Slice subsequent lists from 1:
                    continue
                original_names.append(name.text)
            except AttributeError:
                continue

        deleted = [False] * len(original_names)

        delete_list = root.find("SourceDelete")
        if delete_list:
            for i, delete in enumerate(delete_list[skip_source:]):
                try:
                    if delete.text == "DEL":
                        deleted[i] = True
                except AttributeError:
                    continue

        rename_map = {}
        for i, name in enumerate(root.find("RenameSource")[skip_source:]):
            if not deleted[i]:
                original_name = original_names[i]
                try:
                    name = name.text.strip()
                except AttributeError:
                    name = original_name
                rename_map[name] = (
                    denon_const.MAP_HTTP_SOURCE_NAME_TO_TELNET.get(
                        original_name.lower()
                    )
                    or original_name.upper()
                )
        return rename_map

    def make_device_info_dict(self, xml) -> dict:
        """Parse response for information."""
        root = ET.fromstring(xml)
        xmlns = "{urn:schemas-upnp-org:device-1-0}"
        self._device_info[const.INFO_MODEL] = (
            self._device_info.get(const.INFO_MODEL)
            or get_text(root, "ModelName")
            or get_text(root, f"*/{xmlns}modelName")
        )
        self._device_info[const.INFO_MAC] = self._device_info.get(
            const.INFO_MAC
        ) or get_text(root, "MacAddress")
        self._device_info[const.INFO_SERIAL] = self._device_info.get(
            const.INFO_SERIAL
        ) or get_text(root, f"*/{xmlns}serialNumber")
        self._device_info[const.INFO_ZONES] = int(
            self._device_info.get(const.INFO_ZONES)
            or get_text(root, "DeviceZones")
            or "1"
        )
        self._device_info[const.INFO_MANUFACTURER] = self._device_info.get(
            const.INFO_MANUFACTURER
        ) or get_text(root, f"*/{xmlns}manufacturer")
        self._device_info[const.INFO_FRIENDLY_NAME] = self._device_info.get(
            const.INFO_FRIENDLY_NAME
        ) or get_text(root, f"*/{xmlns}friendlyName")

    @staticmethod
    def make_xml_request(commands: list) -> bytes:
        """Prepare XML body for Denon API."""
        xml_parts = ['<?xml version="1.0" encoding="utf-8"?>\n', "<tx>"]
        for i, command in enumerate(commands):
            if (
                i != 0 and i % 5 == 0
            ):  # API allows multiple XML roots, limit 5 commands each
                xml_parts.append("</tx><tx>")
            xml_parts.append(f'<cmd id="1">{command}</cmd>')
        xml_parts.append("</tx>")
        return "".join(xml_parts).encode()


class DenonAVRApi(DenonHTTPApi):
    """Define the Denon/Marantz AVR API."""

    def __init__(self, host, upnp_data):
        super().__init__(host, upnp_data=upnp_data)
        self.port = denon_const.API_PORT
        self._device_info_url = denon_const.API_DEVICE_INFO_URL


class DenonAVRXApi(DenonHTTPApi):
    """Define the Denon/Marantz AVR-X API."""

    def __init__(self, host, upnp_data):
        super().__init__(host, upnp_data=upnp_data)
        self.port = denon_const.API_PORT
        self._device_info_url = denon_const.API_DEVICE_INFO_URL


class DenonAVRX2016Api(DenonHTTPApi):
    """Define the Denon/Marantz AVR-X 2016 API."""

    def __init__(self, host, upnp_data):
        super().__init__(host, upnp_data=upnp_data)
        self.port = denon_const.API_2016_PORT
        self._device_info_url = denon_const.API_2016_DEVICE_INFO_URL


def get_text(root: ET.Element, tag: str):
    """Get the text attribute if it exists."""
    elem = root.find(tag)
    if elem is not None:
        return elem.text
    return None
