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

OrbitalComs is a fully featured application capable of managing the communications of a Purdue Orbital mission. OrbitalComs can be thought of as the kernel of a program where different user interfaces and communication strategies can be selected to fit a user's needs.

As such, OrbitalComs can be launched directly from the command line as a drop in Ground Station. For a brief help statement, from the environment in which you installed OrbitalComs, simply enter:

```sh
$ orbitalcoms -h
```

This will display the command line usage and options for usage. At its most basic usage, OribtalComs

Example serial usage:
```sh
$ orbitalcoms -f headless -i 120 serial --port /dev/ttyUSB0 --baudrate 9600
```


## Usage in a Script

In addition to the command line interface, OrbitalComs is capable of being imported into an existing python project to manage communications. This is most commonly done when a script running on the Launch Station needs to communicate with the ground station. To show how this is done, let's build a very simplistic launch station script capable of communicating with the OrbitalComs command line app.

The first thing that we need to do is import OrbitalComs and create an instance of a Launch Station using a serial interface to facilitate communications throughout the mission over a serial connection. Luckily OrbitalComs provides a host of common use constructor functions to be used from the get-go.

```py
from orbitalcoms import create_serial_launch_station

# Creating a new Launch Station in a script
LS = create_serial_launch_station(port="/dev/ttyUSB0", baudrate=9600)
```

Next we need to make sure that our Launch Station can receive and process messages sent from the Ground Station. We can do this by binding a list to the Launch Station where incoming messages will be queued.


```py
# Set up to receive messages
message_queue = []
LS.bind_queue(message_queue)
```

We can now process incoming messages by simply checking if the `message_queue` list is populated, and we can process them in the order that they were received by simply popping messages from the beginning of the list:

```py
# Checking for new messages
if message_queue:
    print(message_queue.pop(0))
```

We also want to be able to send our own messages back to the Ground Station. OrbitalComs Stations will take any `ComsMessage`, message conforming dictionary, or message conforming JSON-like string, and try to coerce it into a ComsMessage to be sent.

```py
# Formulate a message
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

# Send it to the GS
LS.send(message)
```

We may also want to be able to check on the progress of a mission without needing to wait for new incoming messages or cluttering our code with excess variables to keep track of state. Luckily, OrbitalComs Stations will keep track of mission progress internally and can be queried by simply checking the corresponding properties on the Station.

Note that in general, OrbitalComs will assume that the Ground Station is the source of truth for mission progress and state, and the Launch Stations is the source of truth for the latest and most accurate data.

```py
# Latest flags and data
print(LS.abort)     # Prints True/False depending on what the GS has sent
print(LS.last_data) # Prints "{'Anything': 'JSON-able'}"
```

Finally, we may want to automatically send our mission state to the Ground Station automatically after some interval of time. This can be tricky, especially if we need to manage multiple threads, processes, or any sort of asynchronous code. Luckily this is a pre-built functionality with OrbitalComs and we can automatically set up our station to resend the most recently sent message every 2 minutes with the following line of code.

```py
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

At this point it is highly recommended that you create a virtual environment so that your changes do not pollute your system version of python. This can be done using `virtualenv`, `conda`, or some other environment manager, but the simplest solution is simply use the python `venv` module.

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

At this point you should be completely set up for development. As a test, you can try running the following commands.

```sh
 $ python3 -c 'import orbitalcoms'  # should not return an error
 $ make test                        # will run the test suite.
 ```


### Contribution Guidelines

Once you have made your changes to the code and ready to push it back into the code base, there are few things you should check before you open a pull request:

  1. Your code should be well tested. If you have modified existing code the existing test suite should pass. If you have added new functionality you should have written new tests under the `tests` directory. Running `make test` should result in a passing test suite and `make test-cov` should not result in a code coverage under 80%

  2. Your code should be well documented. All user facing classes and methods should have docstrings explaining what they do. If a method is too complicated to explain in a reasonable length consider breaking it into sub-methods. Remember to abide by SOLID and DRY principles when possible. If, and only if, it is not trivial to tell what a block of code is doing, add some in line comments. DO NOT OVER COMMENT YOUR CODE. Comments should explain 'why' not 'how' your code works.

  3. Your code should be typed. OrbitalComs is a statically typed package and should be able to pass a strict static analysis from `make type`. In the very rare case it is absolutely necessary to opt out of the type checking system, be sure to leave a comment beside where that is done to explain why.

  4. Your code should be styled. Be sure to run `make style-all` to style your code and test suite to OrbitalComs standards and address any errors that may be reported during this step.

If you have made it this far, it looks like you are ready to open a new pull request. On Github, open a new PR merging your branch into `orbitalcoms/develop`, attach any issues you may have been addressing, and request a review from a qualified reviewer. Our reviewers will look over your code and request changes as they see fit. Once it has met their satisfaction, they will approve your changes and you will be able to merge your branch.


