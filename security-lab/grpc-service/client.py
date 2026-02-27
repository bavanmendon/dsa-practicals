import grpc
import myitems_pb2
import myitems_pb2_grpc
import time

def run():
	channel = grpc.insecure_channel('[::]:50051')
	stub = myitems_pb2_grpc.ItemServiceStub(channel)

	print("=" * 50)
	print("1. UNARY RPC: GetItemById")
	print("=" * 50)
	try:
		response = stub.GetItemById(myitems_pb2.ItemRequest(id=1))
		print(f"Response: ID={response.id}, Name={response.name}")
	except grpc.RpcError as e:
		print(f"Error: {e.code()} - {e.details()}")

	print("\n" + "=" *50)
	print("2. SERVER_STREAMING RPC: ListAllItems")
	print("=" * 50)
	for item in stub.ListAllItems(myitems_pb2.Empty()):
		print(f"Item: ID={item.id}, Name={item.name}")

	print("\n" + "=" * 50)
	print("3. CLIENT-STREAMING RPC: AddItems")
	print("=" * 50)

	def generate_items():
		items_to_add = [
			myitems_pb2.ItemRequest(name="Zoey"),
			myitems_pb2.ItemRequest(name="Prapti"),
			myitems_pb2.ItemRequest(name="Bavan")
		]
		for item in items_to_add:
			print(f"Sending: {item.name}")
			yield item
			time.sleep(0.1)

	result = stub.AddItems(generate_items())
	print(f"Total items added: {result.total_count}")

	print("\n" + "=" * 50)
	print("4. BIDIRECTIONAL STREAMING RPC: ChatAboutItems")
	print("=" * 50)

	def generate_messages():
		messages = ["Hello", "How are you?", "Goodbye"]
		for msg in messages:
			print(f"Client sending: {msg}")
			yield myitems_pb2.ChatMessage(content=msg)
			time.sleep(0.5)

	responses = stub.ChatAboutItems(generate_messages())
	try:
		for response in responses:
			print(f"Server replied: {response.content}")
	except grpc.RpcError as e:
		print(f"gRPC Error: {e.code()}")
		print(f"Details: {e.details()}")

	channel.close()

if __name__ == '__main__':
	run()
