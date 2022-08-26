# =========================================================================== #
# gRPC ReRo Board IO Server Implimentation
# =========================================================================== #
# Copyright(C) 2022 Reverb Robotics Inc.
# Author: Christopher Perlette
# Email: chris.perlette@reverbrobotics.ca
# Alt Email (If there is no response from Chris):  lukas@reverbrobotics.ca
# =========================================================================== #
from concurrent import futures
import threading
import RPi.GPIO as GPIO
import board
import busio
import adafruit_mpr121
import time

import grpc
import rero_io_grpc.lighting_pb2 as lpb
import rero_io_grpc.lighting_pb2_grpc as lpb_grpc
import rero_io_grpc.touch_pb2 as tpb
import rero_io_grpc.touch_pb2_grpc as tpb_grpc


# GRPC integration for lighting control, note, the ledPin is set according to the configuration of the users board
class light_control(lpb_grpc.LightingServicer):
	def __init__(self,intervalOn=750,intervalOff=750,pulseSpeed=20,pulseUpper=90,pulseLower=10,ledPin):
		# Initilize variables
		self.stop_thread=False
		self.led_pin=ledPin
		self.interval_off=intervalOff
		self.interval_on=intervalOn
		self.pulse_speed=pulseSpeed
		self.pulse_upper=pulseUpper
		self.pulse_lower=pulseLower

		# Define lighting state identifiers and handles
		self.handles={
			"on": self.light_on,
			"off": self.light_off,
			"blink": self.light_blink,
			"pulse": self.light_pulse
		}

		# Set up LED power and PWM
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.led_pin, GPIO.OUT)
		self.led_pwm=GPIO.PWM(self.led_pin, 500)
		self.led_pwm.start(0)

		# Initilize the LED thread
		self.led_thread=threading.Thread(target=self.light_off)
		self.led_thread.start()

	def light_on(self):
		# Turn the light on
		self.led_pwm.ChangeDutyCycle(100)
		while True:
			# If there is a state change, end the loop
			if self.stop_thread:
				break
		
	def light_off(self):
		# Turn the light off
		self.led_pwm.ChangeDutyCycle(0)
		while True:
			# If there is a state change, end the loop
			if self.stop_thread:
				break

	def light_blink(self):
		# Initilize time (in milliseconds) and state
		t1=int(round(time.time()*1000))
		state='off'
		while True:
			# Set current time
			t2=int(round(time.time()*1000))

			# If the light is off and appropriate interval has passed, turn the light on
			if (state=='off') and (abs(t1-t2)>=self.interval_on):
				self.led_pwm.ChangeDutyCycle(100)
				t1=t2
				state='on'

			# If the light is off and appropriate interval has passed, turn the light off
			elif (state=='on') and (abs(t1-t2)>=self.interval_off):
				self.led_pwm.ChangeDutyCycle(0)
				t1=t2
				state='off'

			# If there is a state change, end the loop
			if self.stop_thread:
				break

	def light_pulse(self):
		# Initilize the pulse brightness and modifier
		val=self.pulse_lower
		mod=1

		# Initilize the time (in milliseconds)
		t1=int(round(time.time()*1000))
		while True:
			# Set current time
			t2=int(round(time.time()*1000))

			# If enough time has passed, update the pulse width value
			if abs(t1-t2)>=20:
				val+=mod
				self.led_pwm.ChangeDutyCycle(val)
				t1=t2
				# If the light has hit one of the ends, change the direction
				if val<=self.pulse_lower or val>=self.pulse_upper:
					mod=mod*-1

			# If there is a state change, end the loop
			if self.stop_thread:
				break

	def GetLightingChange(self, request, context):
		# Check for invalid lighting state
		if request.newState.lower() not in self.handles.keys():
			# If invalid, return invalid status
			return lpb.Status(status="Invalid Lighting State")

		# State is valid
		else:
			# Kill the old thread and reset stop_thread
			self.stop_thread=True
			self.led_thread.join()
			self.stop_thread=False

			# start the next thread and return success
			self.led_thread=threading.Thread(target=self.handles[request.newState.lower()])
			self.led_thread.start()
			return lpb.Status(status="Lighting State: %s" % request.newState.lower())

	def kill_class(self):
		# Kill the running thread and turn off the light
		self.stop_thread=True
		self.led_thread.join()
		self.led_pwm.ChangeDutyCycle(0)


# GRPC integration for touch detection
class touch_detection(tpb_grpc.TouchServicer):
	def __init__(self,capacitiveTouchPowerPinID=14,capacitiveTouchSensingPinID=11,CTThreashold=60,multiTapDelay=250):
		# Set up GPIO
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)

		# Provide power to the breakout board
		self.power_pin=capacitiveTouchPowerPinID
		GPIO.setup(self.power_pin, GPIO.OUT, initial=GPIO.HIGH)

		# Set up I2C, working on figuring out how to manipulate values so we can connect to different GPIO pins. I'm fairly certain you can just provide the GPIO number, but this has not been tested
		i2c=busio.I2C(board.SCL, board.SDA)
		self.mpr121=adafruit_mpr121.MPR121(i2c)

		# Set up remaining variables
		self.sense_pin=capacitiveTouchSensingPinID
		self.capacitive_threashold=CTThreashold
		self.mtap_delay=multiTapDelay

	def GetTouchRequest(self, request, context):
		# Set up variables for execution
		time_out=int(round(request.timeOut*1000))
		t_count=0
		last_touch=None
		t1=int(round(time.time()*1000))
		flag=True
		t_flag=True

		# "Infinite" loop
		while True:
			# Update current time and CT value
			t2=int(round(time.time()*1000))
			val=abs(self.mpr121.baseline_data(self.sense_pin)-self.mpr121.filtered_data(self.sense_pin))

			# Check for touch
			if val>self.capacitive_threashold and flag:
				# If touched, update time, touch count, and flags
				last_touch=int(round(time.time()*1000))
				t_count+=1
				t_flag=False
				flag=False

			# Prevent multiple detected touches
			if val<self.capacitive_threashold and not flag:
				flag=True

			# Need to do it this way to avoid doing math on a Nan variable
			if last_touch!=None:
				# check if the multi-tap delay as elapsed and return if it has
				if int(round(time.time()*1000))>last_touch+self.mtap_delay:
					return tpb.TouchResponse(status="Touched",count=t_count)

			# Check for time out, t_flag makes sure it doesn't cut off an input
			if abs(t1-t2)>time_out and t_flag:
				return tpb.TouchResponse(status="Timed Out",count=t_count)

	def kill_class(self):
		# Turn off CT breakout, I do it this way so I don't have to write a destructor
		GPIO.output(self.power_pin,GPIO.LOW)


#Server example code, modify at will
def serve():
	# Do this for the finally statement, ledPin is set according to my hardware configuration
	lController=light_control(ledPin=11)
	tController=touch_detection()
	try:
		print("Initilizing server...")
		# Max workers for lighting needs to be 1 so that there isn't any weirdness with controlling the lights
		server=grpc.server(futures.ThreadPoolExecutor(max_workers=1))

		# Add the servicers to the server
		lpb_grpc.add_LightingServicer_to_server(lController, server)
		tpb_grpc.add_TouchServicer_to_server(tController, server)

		# Set up the connection port and start the server
		server.add_insecure_port('[::]:50059')
		server.start()
		print("Server running")
		server.wait_for_termination()

	# Required to turn off the light and CT breakout board on server close. I could write a destructor in the class to do this, but I've never written destructor in python and it's 1AM
	finally:
		if lController!=None:
			lController.kill_class()

		if tController!=None:
			tController.kill_class()

if __name__=="__main__":
	serve()