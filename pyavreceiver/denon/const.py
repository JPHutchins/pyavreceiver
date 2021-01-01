"""Define constants for Denon/Marantz."""

API_DEVICE_INFO_URL = "/goform/Deviceinfo.xml"
API_MAIN_ZONE_XML_STATUS_URL = "/goform/formMainZone_MainZoneXmlStatus.xml"
API_MAIN_ZONE_XML_URL = "/goform/formMainZone_MainZoneXml.xml"
API_PORT = 80

API_2016_PORT = 8080
API_2016_DEVICE_INFO_URL = "/goform/Deviceinfo.xml"

CLI_PORT = 23

MESSAGE_INTERVAL_LIMIT = 50  # milliseconds
MESSAGE_RESPONSE_TIMEOUT = 250  # milliseconds

TELNET_SEPARATOR = "\r"

TELNET_PORT = 23
DEFAULT_TIMEOUT = 10.0
DEFAULT_RECONNECT_DELAY = 10.0
DEFAULT_HEART_BEAT = 10.0

DEVICE_INFO_ENDPOINTS = [
    ":80/goform/Deviceinfo.xml",
    ":8080/goform/Deviceinfo.xml",
]

DEVICE_INFO_SEARCH = {"model": ["ModelName", "ManualModelName"]}

# Valid source on auxiliary zones that follows main zone
SOURCE_FOLLOW = "SOURCE"

SOURCE_AUX = "AUX1"
SOURCE_BLURAY = "BD"
SOURCE_BLUETOOTH = "BT"
SOURCE_CABLE = "SAT/CBL"
SOURCE_DVD = "DVD"
SOURCE_IPOD = "IPD"
SOURCE_USB_IPOD = "USB/IPOD"
SOURCE_GAME = "GAME"
SOURCE_MEDIA_PLAYER = "MPLAY"
SOURCE_NETWORK = "NET"
SOURCE_PHONO = "PHONO"
SOURCE_TUNER = "TUNER"
SOURCE_TV_AUDIO = "TV"
SOURCE_USB = "USB"

MAP_HTTP_SOURCE_NAME_TO_TELNET = {
    "aux": SOURCE_AUX,
    "blu-ray": SOURCE_BLURAY,
    "bluetooth": SOURCE_BLUETOOTH,
    "cbl/sat": SOURCE_CABLE,
    "dvd": SOURCE_DVD,
    "fm": SOURCE_TUNER,
    "ipod": SOURCE_IPOD,
    "ipod/usb": SOURCE_USB_IPOD,
    "game": SOURCE_GAME,
    "media player": SOURCE_MEDIA_PLAYER,
    "network": SOURCE_NETWORK,
    "phono": SOURCE_PHONO,
    "tuner": SOURCE_TUNER,
    "tv audio": SOURCE_TV_AUDIO,
    "usb": SOURCE_USB,
}

TELNET_QUERY = "?"

ATTR_DYNAMIC_EQ = "audyssey_dynamic_eq"

XML_MODEL_NAME = "ModelName"
XML_MAC_ADDRESS = "MacAddress"
XML_ZONE_COUNT = "DeviceZones"
XML_API_VERS = "CommApiVers"
