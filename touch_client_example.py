# =========================================================================== #
# gRPC ReRo Board IO Capacitive Touch Client Example
# =========================================================================== #
# Copyright(C) 2022 Reverb Robotics Inc.
# Author: Christopher Perlette
# Email: chris.perlette@reverbrobotics.ca
# Alt Email (If there is no response from Chris):  lukas@reverbrobotics.ca
# =========================================================================== #
import grpc
import rero_io_grpc.touch_pb2 as tpb
import rero_io_grpc.touch_pb2_grpc as tpb_grpc

def run():
	# Set up channel on the appropriate port
	with grpc.insecure_channel("localhost:50059") as channel:
		# Get stub
		stub=tpb_grpc.TouchStub(channel)

		# Set up a touch request. The timeOut will determine how long in seconds the server waits for a touch input,
		request=tpb.TouchRequest(timeOut=10)
		response=stub.GetTouchRequest(request)
		print(response)

		# Second request for testing purposes
		request=tpb.TouchRequest(timeOut=10)
		response=stub.GetTouchRequest(request)
		print(response)

if __name__=='__main__':
	run()