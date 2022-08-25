#import json
from concurrent import futures
import threading
import RPi.GPIO as GPIO
import time

import grpc
import rero_grpc.lighting_pb2 as lpb
import rero_grpc.lighting_pb2_grpc as lpb_grpc


class light_control(lpb_grpc.LightingServicer):
	def __init__(self,intervalOn=750,intervalOff=750,pulseSpeed=20,pulseUpper=90,pulseLower=10,ledPin=11):
		# Initilize variables
		self.stop_thread=False
		self.led_pin=ledPin
		self.interval_off=intervalOff
		self.interval_on=intervalOn
		self.pulse_speed=pulseSpeed
		self.pulse_upper=pulseUpper
		self.pulse_lower=pulseLower
		self.handles={
			"on": self.light_on,
			"off": self.light_off,
			"blink": self.light_blink,
			"pulse": self.light_pulse
		}

		# Set up LED power
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.led_pin, GPIO.OUT)

		self.led_pwm=GPIO.PWM(self.led_pin, 500)
		self.led_pwm.start(0)

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
		# Work in progress
		if request.newState.lower() not in self.handles.keys():
			return lpb.Status(status="Invalid Lighting State")

		else:
			self.stop_thread=True
			self.led_thread.join()
			self.stop_thread=False

			self.led_thread=threading.Thread(target=self.handles[request.newState.lower()])
			self.led_thread.start()
			return lpb.Status(status="Lighting State: %s" % request.newState.lower())

	def kill_class(self):
		self.stop_thread=True
		self.led_thread.join()
		self.led_pwm.ChangeDutyCycle(0)


def serve():
	# Do this for the finally statement
	controller=light_control()
	try:
		# Max workers needs to be 1 so that there isn't any weirdness with controlling the lights
		server=grpc.server(futures.ThreadPoolExecutor(max_workers=1))
		lpb_grpc.add_LightingServicer_to_server(controller, server)
		server.add_insecure_port('[::]:50059')
		server.start()
		server.wait_for_termination()

	finally:
		if controller!=None:
			controller.kill_class()

if __name__=="__main__":
	serve()