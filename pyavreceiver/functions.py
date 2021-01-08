"""Functions for pyavreceiver."""


def identity(arg, **kwargs):
    """The identity function returns the input."""
    # pylint: disable=unused-argument
    return arg


async def none() -> None:
    """Awaitable that immediately resolves to None."""
    return None
