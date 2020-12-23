"""Define constants."""

__title__ = "pyavreceiver"
__version__ = "0.0.1"


CLI_PORT = 23
DEFAULT_TIMEOUT = 10.0
DEFAULT_RECONNECT_DELAY = 10.0
DEFAULT_HEART_BEAT = 11.0
DEFAULT_STEP = 5

STATE_CONNECTED = "connected"
STATE_DISCONNECTED = "disconnected"
STATE_RECONNECTING = "reconnecting"

# Using ^ as escape character
COMMAND_NAME = "^name"
COMMAND_PARAMS = "^params"
COMMAND_RANGE = "^range"
COMMAND_FUNCTION = "^function"
COMMAND_ZERO = "^zero"

EVENT_TELNET = "telnet"
EVENT_DISCONNECTED = "disconnected"
EVENT_CONNECTED = "connected"

SIGNAL_STATE_UPDATE = "state_update"
SIGNAL_TELNET_EVENT = "telnet_event"
SIGNAL_STATE_UPDATE = "state_update"


ATTR_POWER = "power"
ATTR_VOLUME = "volume"
ATTR_VOLUME_UP = "volume_up"
ATTR_VOLUME_DOWN = "volume_down"
ATTR_LFE_LEVEL = "lfe_level"
ATTR_MUTE = "mute"
ATTR_SOURCE = "source"
ATTR_SOUND_MODE = "sound_mode"
ATTR_SUBWOOFER_ONE = "subwoofer_1"
ATTR_TONE_CONTROL = "tone_control"
ATTR_TREBLE = "treble"
ATTR_BASS = "bass"
ATTR_DIALOG_LEVEL = "dialog_level"
ATTR_DSP_DRC = "dsp_dynamic_range_control"
ATTR_DSP_MODE = "dsp_mode"
ATTR_META_DRC = "meta_dynamic_range_control"

VAL_DOWN = "down"
VAL_UP = "up"

FUNCTION_VOLUME = "volume"
FUNCTION_NUM_TO_DB = "num_to_db"
FUNCTION_DB_TO_NUM = "db_to_num"

MESSAGE_INTERVAL_LIMIT = 50  # milliseconds
