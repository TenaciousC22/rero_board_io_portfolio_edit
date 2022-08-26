# ReRo Board IO gRPC Examples
This repo contains the server used for physical IO on the Reverb Robotics board as well as examples for connecting to and executing calls using python gRPC

## Dependencies
This code requires gRPC, RPi.GPIO, and adafruit-mpr121. Install them with

```
sudo pip3 install grpcio==1.37.1
sudo pip3 install RPi.GPIO
sudo pip3 install adafruit-circuitpython-mpr121
pip3 install grpcio==1.37.1
```

The gRPC module does not have to be installed twice, however it is best practice to not run a command with sudo unless necessary, and the server needs sudo but the clients don't. For this reason we install gRPC in both the sudo and regular user scopes.

## Usage
Run the server with the command ```sudo python3 io_server.py``` This code must be run with sudo as some of the harware accessing code requires super user access.

### Lighting Control
The [lighting control example](https://github.com/reverbrobotics/rero_board_io/blob/main/lighting_client_example.py) contains examples of how to set up a connection with the gRPC server and execute lighting change requests. Currently the implimented patterns are "on", "off", "blink", and "pulse". The command ```python3 lighting_client_example.py``` will execute the example and show the lighting modes and their responses, including what happens when an invalid lighting state change is requested.

### Touch Detection
The [touch control example](https://github.com/reverbrobotics/rero_board_io/blob/main/touch_client_example.py) contains examples of how to set up a connection with the gRPC server and request a touch input. The request takes in a timeOut variable that controls how long the server waits before timing out the touch input request. There is support for multi-tap where the server can count the number of quick, consecutive taps. The command ```python3 touch_client_example.py``` runs the example file which contains two touch requests on a 10 second time out.