# OrbitalComs

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintainer](https://img.shields.io/badge/Maintainer-purdue--orbital-brightgreen)](https://github.com/purdue-orbital)
![GitHub Last Commit](https://img.shields.io/github/last-commit/purdue-orbital/orbitalcoms)
![Tests](https://github.com/purdue-orbital/orbitalcoms/actions/workflows/tests.yml/badge.svg)

Python package from managing communications between Purdue Orbital's Launch Station and Ground Station.

## How to Install

```sh
pip install 'git+https://github.com/purdue-orbital/orbitalcoms#egg=orbitalcoms'
```

## How to Use OrbitalComs

As an app:
```sh
orbitalcoms [-h] [--frontend FRONTEND] [--interval-send INTERVAL_SEND] {socket,serial}
```

Example serial usage:
```sh
orbitalcoms -f dev -i 120 serial --port /dev/ttyUSB0 --baudrate 9600
```

For more help:
```sh
orbitalcoms -h
```


## Usage in a Script

In a script:
```py
from orbitalcoms import create_serial_launch_station

# Creating a new Launch Station in a script
LS = create_serial_launch_station(port="/dev/ttyUSB0", baudrate=9600)

# Set up to receive messages
message_queue = []
LS.bind_queue(message_queue)

# Checking for new messages
if message_queue:
  print(message_queue.pop(0))

# Sending a message
message = {
  "ARMED": 1,
  "ABORT": 0,
  "LAUNCH": 0,
  "STAB": 0,
  "QDM": 0,
  "DATA": {
    "Anything": "trivially serializable",
  },
}
LS.send(message)

# Latest flags and data
print(LS.abort)     # Prints True/False depending on what the GS has sent
print(LS.last_data) # Prints "{'Anything': 'trivially serializable'}" 

# Automatically re-send most recently sent message every 2 minutes
LS.set_send_interval(120)
```

## Architecture
TODO

## Contributions

### Set up
Fork or clone OrbitalComs repo. TODO: more here

### Coding Standards
All contributions must pass the following commands
```ssh
make type
make style-all
```