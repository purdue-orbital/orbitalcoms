<p align="center">
  <img src="https://images.squarespace-cdn.com/content/v1/56ce2044d210b8716143af3a/1521699104186-NCS4AA7ZIS0HFGQP1VMZ/Logo1.png?format=1500w">
</p>


[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintainer](https://img.shields.io/badge/Maintainer-purdue--orbital-brightgreen)](https://github.com/purdue-orbital)
![GitHub Last Commit](https://img.shields.io/github/last-commit/purdue-orbital/orbitalcoms)
![Tests](https://github.com/purdue-orbital/orbitalcoms/actions/workflows/tests.yml/badge.svg)

# OrbitalComs

OrbitalComs is a python package for managing communications between Purdue Orbital's Launch Station and Ground Station.

## How to Install

To get the most recent and up to date version of OrbitalComs and be on the cutting edge of development, we recomend installing the package directly from github. This can be done simply through pip, though you will need to have git installed.

```sh
$ pip install 'git+https://github.com/purdue-orbital/orbitalcoms#egg=orbitalcoms'
```


## How to Use OrbitalComs

OrbitalComs is a fully featured application capable of managing the commumications of a Purdue Orbital mission. OrbitalComs can be thought of as the kernal of a program where different user interfaces and communication strategies can be selected to fit a users needs.

As such, OrbitalComs can be launched dricetly from the command line as a drop in Ground Station. For a brief help statment, from the enviormnet in which you installed OrbitalComs, simply enter:

```sh
$ orbitalcoms -h
```

This will display the command line usage and options for usage. At its most basic usage, OribtalComs

Example serial usage:
```sh
$ orbitalcoms -f headless -i 120 serial --port /dev/ttyUSB0 --baudrate 9600
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
    "Anything": "JSON-able",
  },
}
LS.send(message)

# Latest flags and data
print(LS.abort)     # Prints True/False depending on what the GS has sent
print(LS.last_data) # Prints "{'Anything': 'JSON-able'}"

# Automatically resend most recently sent message every 2 minutes
LS.set_send_interval(120)
```

## Contributions

OrbitalComs is an open source development project and as such all contributions are both welcome and highly appreciated. Below you will find information regarding how to get set up and start contributing.

### Set up

First begin by forking or cloning the OrbitalComs repository. After having done, navigate to the created directory.

```sh
$ git clone https://github.com/purdue-orbital/orbitalcoms.git orbitalcoms
$ cd orbitalcoms
```

At this point it is highly recommended that you create a virtual environment so that your changes do not pollute your system version of python. This can be done using `virtualenv`, `conda` or some other environment manager, but the simplest solution is simply use the python `venv` module.
You can create and activate a virtual environment using the following command.

```sh
$ python3 -m venv venv && . venv/bin/activate
```

Rember, this environment should be created using one of the versions of python supported by OrbitalComs.

The next step is to install OrbitalComs in development mode. This can be done by hand by using pip.

```sh
$ pip install -e .[dev]
```

This can also be done by instead using the target in the Makefile, provided for convenience.

```sh
$ make dev
```

At this point you should be completely set up for development. As a test, you can try running the following the commands.

```sh
 $ python3 -c 'import orbitalcoms'  # should not return an error
 $ make test                        # will run the test suite.
 ```


### Contribution Guidelines

TODO
