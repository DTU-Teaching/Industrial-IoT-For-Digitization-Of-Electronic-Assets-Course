# Module 1: PLC Connection and Modbus Data Exchange

## Introduction

Welcome to the demo where you will learn to deal with industrial controllers and protocols. This hands-on demonstration
aims to provide you with real-world experience in connecting a PLC to a virtual pump station and exchanging data using
the Modbus protocol. Throughout this session, you will encounter various technologies commonly used in industrial
settings.

## Goals of today's demo

* Establish a connection between a PLC and a virtual pump station.
* Implement data exchange using the Modbus protocol.
* Gain hands-on experience with technologies such as SSH for remote development.
* Ensure secure connections from anywhere using Tailscale.
* Understand and handle data conversion between little and big endian formats.
* Develop a Modbus TCP client using PyModbus.

# Connect to the PLC

Every group should have access to a PLC. As you can see, the device is not connected to any screen. This is typical for
industrial settings where the PLC is usually installed in a cabinet and connected to a network. To configure the PLC and
run your own programs on it, we still need to see what is going on with the device. To do this, we will make use of a
protocol called SSH.

SSH is a cryptographic network protocol for operating network services securely over an unsecured network. Typical
applications include remote command-line, login, and remote command execution.

You can connect to the PLC if you are connected to the switch in the classroom by using the following host:
```raspberrypi-grpx-client``` where you replace x with your group number, the default username is ```pi``` and the password you can ask to the teacher.

Almost all Unix-based systems come with an SSH client preinstalled. You can check if you have one by typing ```ssh -V```
in your terminal. If you don't have one, you can install it by typing ```sudo apt install openssh-client``` for
Debian-based systems.

Now connect an Ethernet cable to the PLC and your computer, and open a terminal. To connect to the PLC,
type ```ssh pi@raspberrypi-grpx-client``` and enter the password. You should now be connected to the PLC and
see a terminal prompt like this: ```pi@raspberrypi:~ $```. You can now run commands on the PLC.

The first step is to change the default password. To do this, type ```passwd``` and follow the instructions.

## Public-Private Key Authentication

A more convenient and secure way to connect to the PLC through SSH is with a public-private key pair. This way, you
don't have to type in your password every time you want to connect to the PLC. If you are interested in how
public/private keys work in-depth, watch the following video:

[//]: # (inlcude image with link to video)
<a href="https://www.youtube.com/watch?v=GSIDS_lvRv4"><img width="691" height="342" src="media/video.png" style="display: block; margin: 0 auto" alt="Computerphile video"></a>

To do this, we first need to generate a key pair. You can do this by typing ```ssh-keygen``` in the terminal of your own
computer. You will be asked to enter a file name for the key pair. You can leave the default value by pressing enter.
You will also be asked to enter a passphrase. You can leave this empty by pressing enter.

Now you should have two files in your home directory. One called ```id_rsa``` and one called ```id_rsa.pub```. The first
one is your private key, and the second one is your public key. Now we need to copy the public key to the PLC. To do
this, we can use the ```ssh-copy-id``` command. Type ```ssh-copy-id pi@raspberrypi-grpx-client``` and enter the password. From now
on, you can connect to the PLC without entering a password. Try it out by typing ```ssh pi@raspberrypi-grpx-client```.

## Remote Development

One problem with the current setup is that we need to be connected to the PLC with an Ethernet cable. This is not very
convenient. To solve this problem, we will use a tool called Tailscale. Tailscale is a mesh VPN that makes it easy to
connect your devices. It works by installing a small program on your device that creates a virtual network interface.
This interface is then used to connect to other devices.

To install Tailscale on the PLC, SSH into it and execute the following command:

```sh
curl -fsSL https://tailscale.com/install.sh | sh
```

After the installation is complete, run

```sh
sudo tailscale up
```

to start Tailscale. You will be asked to authenticate with the URL in the terminal. Create an account. Once you have an
account on Tailscale, you can go to the admin console in the browser, and you will see the PLC in the list of devices.
Click on the PLC and press share. Share this link with your group members so they can also connect to the PLC.

Now, install the Tailscale client on your PC and log in with your previously created account. If you are running Linux,
you can do it in the same way as before:

```sh
curl -fsSL https://tailscale.com/install.sh | sh
```

To learn more about Tailscale, visit their website: [https://tailscale.com/](https://tailscale.com/)

## Modbus

As discussed in the slides before, Modbus has 4 types of registers:

- Coils (Discrete Output)
- Discrete Inputs
- Input Registers
- Holding Registers

The discrete input and output registers are 1 bit long. The input and holding registers are 16 bit long. For this demo,
we are going to work with the Input and Holding registers. The input registers are read-only and are used by the PLC to
write sensor data to. The holding registers are writable, and the PLC uses those to take control inputs from other
devices. The goal today is to read all sensor data from the Input registers and take control over the pump by writing to
the holding registers.

The pump station is configured with the following registers:

### Input Registers (Sensor Data)

| **Reg. addr.** | **Signal**       | **Unit** | **Data type** | **Range**  | **# of regs** | **Description**                         |
|----------------|------------------|----------|---------------|------------|---------------|-----------------------------------------|
| 0              | External Control | Bool     | uint16        | [0, 1]     | 1             | If 0 self-control If 1 external Control |
| 1              | Pump 1 Speed     | rpm      | uint32        | [0, 1500]  | 2             | Speed of pump 1                         |
| 3              | Pump 1 Power     | kW       | float32       | [0, 50.00] | 2             | Power of pump 1                         |
| 5              | Pump 1 Outflow   | m3/h     | float32       | [0, Q_max] | 2             | Outflow of pump 1                       |
| 7              | Pump 2 Speed     | rpm      | uint32        | [0, 1500]  | 2             | Speed of pump 2                         |
| 9              | Pump 2 Power     | kW       | float32       | [0, 50.00] | 2             | Power of pump 2                         |
| 11             | Pump 2 Outflow   | m3/h     | float32       | [0, Q_max] | 2             | Outflow of pump 2                       |

### Holding Registers (Control Data)

| **Reg. addr.** | **Signal**          | **Unit** | **Data type** | **Range** | **# of regs** | **Description**                                    |
|----------------|---------------------|----------|---------------|-----------|---------------|----------------------------------------------------|
| 0              | External Control    | Bool     | uint16        | [0, 1]    | 1             | If 0 autonomous Control If 1 takes control signals |
| 1              | Pump 1 Speed Target | rpm      | uint32        | [0, 1500] | 2             | Set target speed for pump 1                        |
| 3              | Pump 2 Speed Target | rpm      | uint32        | [0, 1500] | 2             | Set target speed for pump 2                        |

### Data Encoding and Decoding

The input and holding registers are both 16-bit unsigned integers. This would mean that we can only store integers
between 0 and 65535. To store floating-point numbers or larger integers, we need to split them up into multiple
registers. We can do this by encoding the data into a byte array using the Big Endian format.

We will provide the Python code to encode and decode the data.

**Encode 32-bit unsigned int**

```python
import struct


def encode_32_bit_integer(value):
    byte_value = struct.pack('>I', int(value))
    return struct.unpack('>HH', byte_value)
```

**Encode 32-bit float**

```python
import struct


def encode_32_bit_float(value):
    byte_value = struct.pack('>f', float(value))
    return struct.unpack('>HH', byte_value)
```

**Decode 32-bit unsigned int**

```python
import struct


def decode_32_bit_integer(registers):
    handle = [struct.pack('>H', p) for p in registers]
    binary_string = b''.join(handle)
    return struct.unpack('!I', binary_string)[0]
```

**Decode 32-bit float**

```python
import struct


def decode_32_bit_float(registers):
    handle = [struct.pack('>H', p) for p in registers]
    binary_string = b''.join(handle)
    return struct.unpack('!f', binary_string)[0]
```

### PyModbus

Pymodbus is a Python library that provides a client to communicate with Modbus devices. You can install it by typing

```sh
pip install pymodbus
```

in your terminal. You can find a lot of examples on their
documentation [https://pymodbus.readthedocs.io/en/latest/index.html](https://pymodbus.readthedocs.io/en/latest/index.html),
but we will cover the basics here.

The first step is to create a client.

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('<Replace with PLC IP>', port=502)
client.connect()
```

If everything is working, `client.connect()` should return `True`.

You should now be able to read data from the PLC with the `client.read_input_registers` function.

```python
client.read_input_registers(address=0, count=1, unit=0)
```

This will return a ModbusResponse object. You can get the data from this object by calling `.registers` on it.

```python
rr = client.read_input_registers(address=0, count=1, unit=0).registers
```

Remember that the data is

encoded. You can decode it by calling the decode functions we provided earlier.

To write data to the PLC, you can use the `client.write_registers` function.

```python
client.write_registers(address=0, values=(0, 0), unit=0)
```

Again, remember to encode the data before writing it to the PLC.

## Exercise of Today

- Connect to the PLC using SSH
- Connect from anywhere using Tailscale
- Create a Python script that runs on the PLC and reads all sensor data from the input registers. It should decode the
  values and print them to the terminal.
- In the same script, create a function that writes the target speed of pump 1 and 2 to the holding registers and watch
  the pump speed change.