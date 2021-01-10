![AV Receiver Logo](logos/avreceiver_github_small.png)

The goal of pyavreceiver is to provide a universal Python interface for Audio Video Receiver devices regardless of brand and supported protocols.

## Installation
Requires Python >= 3.8

`pip install pyavreceiver`

## Quickstart
`python3 -m asyncio`

```python3
from pyavreceiver import factory
d = await factory("IP address to your receiver, string")
await d.init()
await d.main.update_all()
d.main.power  # get state
await d.main.set_power(True)  # set state
d.main.state
d.main.commands
await d.disconnect()
```

## Supported Devices
- Denon AVRs (alpha)
- Marantz AVRs (alpha)

## Design
pyavreceiver is modeled on, and derivitave of, the [pyheos](https://github.com/andrewsayre/pyheos) project.

Some primary principals:
- Base classes for AVReceiver, Zone, Command, TelnetConnection, Message, HTTPApi should encapsulate the commonalities between devices
- All IO (other than initial file reads) is asynchronous
- pyavreceiver should subscribe to state rather than poll when possible
- A device can have multiple connections or APIs: telnet, HTTP API, websocket, or UPnP
- The connection to the device should heal itself if it is disconnected

## Telnet Queue and Quality of Service
The telnet protocol is useful for maintaining realtime state of an AVR with low latency.  pyavreceiver uses [telnetlib3](https://github.com/jquast/telnetlib3).  Telnet commands are throttled according to manufacturer specification by means of a `PriorityQueue`.  The `PriorityQueue` and related `ExpectedResponseQueue` allow for varying levels of QoS.  For example, a QoS 0 command has no QoS and can in fact be issued synchronously (eg. for rapid incremental volume changes).  

All commands above 0 QoS will add an `ExpectedResponse` to the `ExpectedResponseQueue`.  This `ExpectedResponse` will be cleared from the queue if 1) the device replies to the command or 2) the command expires (retires expended or default expiration of 1.5s exceeded).  Higher levels of QoS will be executed before lower QoS commands in the queue *even if the lower QoS command was issued first.*  Only two commands, power and mute, are set to the highest QoS level of 3 with most commands at 2.
![QoS Diagram](docs/qos-diagram.svg)

## Contributions
Testing, bug reports, and contributions are welcome.  New devices should be modeled from the denon folder.  A new brand of receiver will inherit from the base classes provided by pyavreceiver.  Command dictionaries, if necessary, should be included in YAML format.
#### Command (commands.py, commands.yaml)
The Command class is responsible for constructing a message to send to the device.  The methods .set_val and .set_query return new instances of the command with an argument set.
#### HTTPApi (http_api.py)
The HTTPApi class should contain methods and commands for interacting with a device using [aiohttp](https://github.com/aio-libs/aiohttp)
#### Message (response.py)
The Message class is responsible for interpreting a message from the device.  There could be TelnetMessage, UpnpMessage, HTTPMessage, etc.
#### Receiver (receiver.py)
The Receiver class can be subclassed to add any unique attributes.
#### TelnetConnection (telnet_connection.py)
The TelnetConnection class must provide a response_handler for receiving telnet messages.
#### Zone (zone.py)
The Zone class can be subclassed to provide extra unique attributes or add alternative command protocols (HTTP, UPnP, etc.) for wide support.
### factory (__init__.py)
Your new device should be identifiable and added to the factory function in __init__.py
