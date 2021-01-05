"""pyavreceiver errors."""


class AVReceiverError(Exception):
    """Base class for library errors."""


class AVReceiverInvalidArgumentError(AVReceiverError):
    """Invalid argument error."""


class AVReceiverIncompatibleDeviceError(AVReceiverError):
    """Invalid argument error."""


class QosTooHigh(AVReceiverError):
    """QoS too high error."""

    def __init__(self):
        self.message = "Highest QoS value is reserved for resent commands."
        super().__init__(self.message)
