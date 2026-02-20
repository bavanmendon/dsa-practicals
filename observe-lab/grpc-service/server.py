import grpc
from concurrent import futures
import time
import myitems_pb2
import myitems_pb2_grpc
from grpc_reflection.v1alpha import reflection
from pymongo import MongoClient
import os

# Prometheus imports
from prometheus_client import start_http_server
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor

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

	def UpdateItem(self, request, context):
		# Unary RPC: Update an existing item in MongoDB
		try:
			print(f"[gRPC] Updating item: id={request.id}, name={request.name}")

			# Update MongoDB
			#doc = {{"id": request.id}, {"$set": {"name": request.name}}}
			result = collection.update_one({"id": request.id}, {"$set": {"name": request.name}})

			if result.matched_count == 0:
				print(f"[gRPC] Item not found: {request.id}")
				context.set_code(grpc.StatusCode.NOT_FOUND)
				context.set_details("Item not found")
				return myitems_pb2.ItemResponse(success=False)

			print(f"[gRPC] Item updated successfully: {request.id}")
			return myitems_pb2.ItemResponse(id=request.id, name=request.name, success=True)

		except Exception as e:
			print(f"[gRPC] Error updating item: {e}")
			context.set_code(grpc.StatusCode.INTERNAL)
			context.set_details(f"Database error: {str(e)}")
			return myitems_pb2.ItemResponse(success=False)

	def DeleteItem(self, request, context):
		# Unary RPC: Delete an existing item in MongoDB
		try:
			print(f"[gRPC] Deleting item: id={request.id}, name={request.name}")

			# Update MongoDB
			#doc = {"id": request.id, "name": request.name}
			result = collection.delete_one({"id": request.id})

			if result.deleted_count == 0:
				print(f"[gRPC]  Item not found: {request.id}")
				context.set_code(grpc.StatusCode.NOT_FOUND)
				context.set_details("Item not found")
				return myitems_pb2.ItemResponse(success=False)

			print(f"[gRPC] Item deleted successfully: {request.id}")
			return myitems_pb2.ItemResponse(id=request.id, name=request.name, success=True)

		except Exception as e:
			print(f"[gRPC] Error deleting item: {e}")
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
	# Start Prometheus HTTP server on port 9103
	start_http_server(9103)
	print("[gRPC] Prometheus metrics server started on port 9103")

	# Created Prometheus interceptor
	prom_interceptor = PromServerInterceptor()

	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=[prom_interceptor])

	# Add servicer to server
	myitems_pb2_grpc.add_ItemServiceServicer_to_server(ItemServiceServicer(), server)

	# Enable gRPC reflection
	service_names = (myitems_pb2.DESCRIPTOR.services_by_name['ItemService'].full_name,
			reflection.SERVICE_NAME)
	reflection.enable_server_reflection(service_names, server)

	# Start server
	server.add_insecure_port('[::]:50051')
	server.start()
	print("[gRPC] Server started on port 50051")
	server.wait_for_termination()

if __name__ == '__main__':
	serve()
