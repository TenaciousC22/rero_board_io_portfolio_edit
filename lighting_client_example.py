import time

import grpc
import rero_grpc.lighting_pb2 as lpb
import rero_grpc.lighting_pb2_grpc as lpb_grpc

def run():
	with grpc.insecure_channel("localhost:50059") as channel:
		stub=lpb_grpc.LightingStub(channel)
		
		# Create lighting change request
		request=lpb.LightingRequest(newState="on")
		response=stub.GetLightingChange(request)
		print(response)
		time.sleep(5)


		request=lpb.LightingRequest(newState="blink")
		response=stub.GetLightingChange(request)
		print(response)
		time.sleep(5)

		request=lpb.LightingRequest(newState="pulse")
		response=stub.GetLightingChange(request)
		print(response)
		time.sleep(5)

		request=lpb.LightingRequest(newState="test")
		response=stub.GetLightingChange(request)
		print(response)
		time.sleep(5)
		
		request=lpb.LightingRequest(newState="off")
		response=stub.GetLightingChange(request)
		print(response)
		time.sleep(5)
		print("Done")

if __name__=='__main__':
	run()