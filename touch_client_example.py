import grpc
import rero_io_grpc.touch_pb2 as tpb
import rero_io_grpc.touch_pb2_grpc as tpb_grpc

def run():
	with grpc.insecure_channel("localhost:50059") as channel:
		stub=tpb_grpc.TouchStub(channel)

		request=tpb.TouchRequest(timeOut=10)
		response=stub.GetTouchRequest(request)
		print(response)

		request=tpb.TouchRequest(timeOut=10)
		response=stub.GetTouchRequest(request)
		print(response)

if __name__=='__main__':
	run()