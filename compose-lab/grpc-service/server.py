import grpc
from concurrent import futures
import time
import myitems_pb2
import myitems_pb2_grpc
from grpc_reflection.v1alpha import reflection
from pymongo import MongoClient
import os

# MongoDB connection
mongo_host = os.environ.get("MONGO_HOST", "localhost")
mongo_port = os.environ.get("MONGO_PORT", "27017")
mongo_db = os.getenv("MONGO_DB", "itemsdb")

client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}", serverSelectionTimeoutMS=5000)
db = client[mongo_db]
collection = db["items"]

# Create unique index on id field
collection.create_index("id", unique=True)

print(f"[gRPC] connected to MongoDB at {mongo_host}:{mongo_port}")

class ItemServiceServicer(myitems_pb2_grpc.ItemServiceServicer):

	def CreateItem(self, request, context):
		# Unary RPC: Create a new item in MongoDB
		try:
			print(f"[gRPC] Creating item: id={request.id}, name={request.name}")

			# Insert into MongoDB
			doc = {"id": request.id, "name": request.name}
			collection.insert_one(doc)

			print(f"[gRPC] Item created successfully: {request.id}")
			return myitems_pb2.ItemResponse(id=request.id, name=request.name, success=True)

		except Exception as e:
			print(f"[gRPC] Error creating item: {e}")
			context.set_code(grpc.StatusCode.INTERNAL)
			context.set_details(f"Database error: {str(e)}")
			return myitems_pb2.ItemResponse(success=False)

	def GetItemById(self, request, context):
		# Get item by ID from MongoDB
		try:
			doc = collection.find_one({"id": request.id})
			if not doc:
				context.set_code(grpc.StatusCode.NOT_FOUND)
				context.set_details("Item not found")
				return myitems_pb2.ItemResponse()

			return myitems_pb2.ItemResponse(id=doc["id"], name=doc["name"], success=True)

		except Exception as e:
			print(f"[gRPC] Error: {e}")
			context.set_code(grpc.StatusCode.INTERNAL)
			context.set_details(str(e))
			return myitems_pb2.ItemResponse(success=False)

	def ListAllItems(self, request, context):
		# Server-streaming RPC: List all items
		try:
			for doc in collection.find():
				yield myitems_pb2.ItemResponse(id=doc["id"], name=doc["name"], success=True)

		except Exception as e:
			print(f"[gRPC] Error: {e}")
			context.set_code(grpc.StatusCode.INTERNAL)
			context.set_details(str(e))

def serve():
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

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
