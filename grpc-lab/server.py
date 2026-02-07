import grpc
from concurrent import futures
import time
import myitems_pb2
import myitems_pb2_grpc
from grpc_reflection.v1alpha import reflection

# In-memory data storage (reuse reflection)
items = [
	{"id": 1, "name": "Kala"},
	{"id": 2, "name": "JP"}
]
next_id = 3

class ItemServiceServicer(myitems_pb2_grpc.ItemServiceServicer):

	def GetItemById(self, request, context):
		# Unary RPC: Get single item by ID
		item = next((i for i in items if i['id'] == request.id), None)
		if item:
			return myitems_pb2.ItemResponse(id=item['id'], name=item['name'])
		else:
			# Set gRPC status code for error handling
			context.set_code(grpc.StatusCode.NOT_FOUND)
			context.set_details(f'Item with ID {request.id} notfound')
			return myitems_pb2.ItemResponse()

	def ListAllItems(self, request, context):
		# Server-streaming RPC: Stream all items to client
		for item in items:
			yield myitems_pb2.ItemResponse(id=item['id'], name=item['name'])

	def AddItems(self, request_iterator, context):
		# Client-streaming RPC: Receive multiple items from client
		global next_id
		count = 0
		for item_request in request_iterator:
			if not item_request.name:
				context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
				context.set_details('Item name cannot be empty')
				return myitems_pb2.ItemsAddedResult(total_count=0)

			new_item = {"id": next_id, "name": item_request.name}
			items.append(new_item)
			next_id += 1
			count += 1

		return myitems_pb2.ItemsAddedResult(total_count=count)
	
	# def generate_messages():
	# 	messages = ["Hi", "I'm fine", "See you"]
	# 	for msg in messages:
	# 		print(f"Server sending: {msg}")
	# 		yield myitems_pb2.ChatMessage(content=msg)
	# 		time.sleep(0.5)
	
	def ChatAboutItems(self, request_iterator,context):
		# Bidirectional-streaming RPC: Receive from and send to Client
		print("[SERVER] ChatAboutItems called")
		try:
			for chat_msg in request_iterator:
				print(f"[SERVER] Received: {chat_msg.content}")

				# Create response
				response = myitems_pb2.ChatMessage(content = f"Server Echo: {chat_msg.content}")
				print(f"[SERVER] Sending: {response.content}")
				yield response
		except Exception as e:
			print(f"[SERVER] Exception in ChatAboutItems: {type(e).__name__: {e}}")
			import traceback
			traceback.print_exc()
			context.set_code(grpc.StatusCode.INTERNAL)
			context.set_details(f"Server error: {str(e)}")
			raise

# Logging Interceptor
class LoggingInterceptor(grpc.ServerInterceptor):
	def intercept_service(self, continuation, handler_call_details):
		print(f"[LOG] Method called: {handler_call_details.method}")
		return continuation(handler_call_details)

def serve():
	# Create server with interceptor
	interceptors = [LoggingInterceptor()]
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors)

	# Add servicer to server
	myitems_pb2_grpc.add_ItemServiceServicer_to_server(ItemServiceServicer(), server)

	# Enable gRPC reflection
	service_names = (myitems_pb2.DESCRIPTOR.services_by_name['ItemService'].full_name,
			reflection.SERVICE_NAME)
	reflection.enable_server_reflection(service_names, server)

	# Start server
	server.add_insecure_port('[::]:50051')
	server.start()
	print("gRPC Server started on port 50051")
	server.wait_for_termination()

if __name__ == '__main__':
	serve()
