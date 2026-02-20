import time
import grpc
import requests
import myitems_pb2
import myitems_pb2_grpc
import requests

def test_rest_performance(iterations=10000):
	# Test REST API performance
	session = requests.Session()
	start_time = time.time()

	for i in range(iterations):
		start=time.time()
		response = requests.get('http://localhost:5000/items/1')
		end = time.time()

	if response.status_code == 200:
		print(f"Time per request: {end - start}")
	else:
		print(f"Request failed with status {response.status_code}")

	end_time = time.time()
	total_time = end_time - start_time
	avg_time = total_time / iterations

	print(f"REST API Results:")
	print(f"	Total time: {total_time:.4f}s")
	print(f"	Average time per call: {avg_time:.4f}s")
	print(f" 	Calls per seconds: {iterations/total_time:.2f}s")
	return total_time

def test_grpc_performance(iterations=10000):
	# Test gRPC performance
	channel = grpc.insecure_channel('localhost:50051')
	stub = myitems_pb2_grpc.ItemServiceStub(channel)

	start_time = time.time()

	for i in range(iterations):
		response = stub.GetItemById(myitems_pb2.ItemRequest(id=1))

	end_time = time.time()
	total_time = end_time - start_time
	avg_time = total_time / iterations

	print(f"\ngRPC Results:")
	print(f"	Total time: {total_time:.4f}s")
	print(f"	Average time per call: {avg_time:.4f}s")
	print(f"	Calls per second: {iterations/total_time:.2f}")

	channel.close()
	return total_time

if __name__ == '__main__':
	print("Performance Comparison: REST vs gRPC")
	print("=" * 50)

	# Ensure REST server os running on port 5000
	rest_time = test_rest_performance(10000)
	grpc_time = test_grpc_performance(10000)

	print(f"\nComparison:")
	print(f"	gRPC is {rest_time/grpc_time:.2f}x faster than REST")
