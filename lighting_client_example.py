# =========================================================================== #
# gRPC ReRo Board IO Lighting Client Example
# =========================================================================== #
# Copyright(C) 2022 Reverb Robotics Inc.
# Author: Christopher Perlette
# Email: chris.perlette@reverbrobotics.ca
# Alt Email (If there is no response from Chris):  lukas@reverbrobotics.ca
# =========================================================================== #

# Need this for testing
import time

# Need this to access the server
import grpc
import rero_io_grpc.lighting_pb2 as lpb
import rero_io_grpc.lighting_pb2_grpc as lpb_grpc

def run():
	# Set up channel on the appropriate port
	with grpc.insecure_channel("localhost:50059") as channel:
		# Get stub
		stub=lpb_grpc.LightingStub(channel)
		
		# Create lighting change request, print the response wait 5 seconds to check behaviour
		request=lpb.LightingRequest(newState="on")
		response=stub.GetLightingChange(request)
		print(response)
		time.sleep(5)

		# Create lighting change request, print the response wait 5 seconds to check behaviour
		request=lpb.LightingRequest(newState="blink")
		response=stub.GetLightingChange(request)
		print(response)
		time.sleep(5)

		# Create lighting change request, print the response wait 5 seconds to check behaviour
		request=lpb.LightingRequest(newState="pulse")
		response=stub.GetLightingChange(request)
		print(response)
		time.sleep(5)

		# Create lighting change request, print the response wait 5 seconds to check behaviour
		request=lpb.LightingRequest(newState="test")
		response=stub.GetLightingChange(request)
		print(response)
		time.sleep(5)

		# Create lighting change request, print the response wait 5 seconds to check behaviour		
		request=lpb.LightingRequest(newState="off")
		response=stub.GetLightingChange(request)
		print(response)
		time.sleep(5)
		print("Done")

if __name__=='__main__':
	run()