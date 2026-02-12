from flask import Flask, request, jsonify
import grpc
import myitems_pb2
import myitems_pb2_grpc
import os
import time
from pybreaker import CircuitBreaker, CircuitBreakerError

app = Flask(__name__)

# gRPC connection configuration
GRPC_HOST = os.getenv("GRPC_HOST", "localhost")
GRPC_PORT = os.getenv("GRPC_PORT", "50051")

# Create gRPC channel and stub
channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
stub = myitems_pb2_grpc.ItemServiceStub(channel)

# Circuit Breaker configuration
breaker = CircuitBreaker(
	fail_max = 3,		# Open after 3 consecutive failures
	reset_timeout = 30	# Half-open after 30 seconds
)

print(f"[REST] Connected to gRPC at {GRPC_HOST}:{GRPC_PORT}")

def grpc_create_item(item_data):
	# Make gRPC call to create item with 1-second timeout
	request = myitems_pb2.ItemRequest(id=item_data["id"], name=item_data["name"])
	return stub.CreateItem(request, timeout=1)

def grpc_update_item(item_data):
	# Make gRPC call to update item with 1-second timeout
	request = myitems_pb2.ItemRequest(id=item_data["id"], name=item_data["name"])
	return stub.UpdateItem(request, timeout=1)

def grpc_delete_item(item_data):
	# Make gRPC call to delete item with 1-second timeout
	request = myitems_pb2.ItemRequest(id=item_data["id"])
	return stub.DeleteItem(request, timeout=1)

@app.route('/items', methods=['POST'])
def create_item():
	# Create item with retry logic and circuit breaker
	# - 3 attempts with exponential backoff (0ms, 100ms, 200ms)
	# - Circuit breaker opens after 3 consecutive failures
	# - Returns 503 when circuit is open

	item_data = request.get_json()

	if not item_data or 'id' not in item_data or 'name' not in item_data:
		return jsonify({"error": "Bad request"}), 400

	# Retry configuration
	max_attempts = 3
	delays = [0, 0.1, 0.2]	# 0ms, 100ms, 200ms

	last_error = None

	for attempt in range(max_attempts):
		try:
			print(f"[REST] Attempt {attempt + 1}/{max_attempts}")

			# Call gRPC through circuit breaker
			response = breaker.call(grpc_create_item, item_data)

			print(f"[REST] Item created successfully: {response.id}")
			return jsonify({"message": "Item created", "id": response.id, "name": response.name}), 201

		except CircuitBreakerError:
			# Circuit is open - fail fast
			print(f"[REST] Circuit breaker is OPEN - failing fast")
			return jsonify({"error": "Service unavailable"}), 503

		except grpc.RpcError as e:
			last_error = e
			print(f"[REST] gRPC Error on attempt {attempt + 1}: {e.code()}")

			# Don't retry on last attempt
			if attempt < max_attempts - 1:
				delay = delays[attempt + 1]
				print(f"[REST] Retrying in {delay}s...")
				time.sleep(delay)

	# All retries exhausted
	print(f"[REST] All retries exhausted. Returning error.")
	return jsonify({"error": "Backend failure", "details": str(last_error)}), 500

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
	# Get item by ID (no retry/circuit breaker for reads
	try:
		request = myitems_pb2.ItemRequest(id=item_id)
		response = stub.GetItemById(request, timeout=1)

		return jsonify({"id": response.id, "name": response.name}), 200

	except grpc.RpcError as e:
		if e.code() == grpc.StatusCode.NOT_FOUND:
			return jsonify({"error": "Item not found"}), 404
		return jsonify({"error": str(e)}), 500

@app.route('/items', methods=['GET'])
def list_items():
	# List all items
	try:
		items = []
		for item in stub.ListAllItems(myitems_pb2.Empty(), timeout=5):
			items.append({"id": item.id, "name": item.name})

		return jsonify(items), 200

	except grpc.RpcError as e:
		return jsonify({"error": str(e)}), 500

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
		# Update specific item with retry logic and circuit breaker
		# - 3 attempts with exponential backoff (0ms, 100ms, 200ms)
		# - Circuit breaker opens after 3 consecutive failures
		# - Returns 503 when circuit is open
		
		item_data = request.get_json()
		
		if not item_data or 'id' not in item_data or 'name' not in item_data or item_data['id'] != item_id:
			return jsonify({"error": "Bad request"}), 400
		
		# Retry configuration
		max_attempts = 3
		delays = [0, 0.1, 0.2]

		last_error = None

		for attempt in range(max_attempts):
			try:
				print(f"[REST] Attempt {attempt + 1}/{max_attempts}")

				# Call gRPC through circuit breaker
				response = breaker.call(grpc_update_item, item_data)

				print(f"[REST] Item updated successfully: {response.id}")
				return jsonify({"message": "Item updated", "id": response.id, "name": response.name}), 201
			
			except CircuitBreakerError:
				# Circuit is open - fail fast
				print(f"[REST] Circuit breaker is OPEN - failing fast")
				return jsonify({"error": "Service unavailable"}), 503
			
			except grpc.RpcError as e:
				last_error = e
				print(f"[REST] gRPC Error on attempt {attempt + 1}: {e.code()}")

				# Don't retry on last attempt
				if attempt < max_attempts - 1:
					delay = delays[attempt + 1]
					print(f"[REST] Retrying in {delay}s...")
					time.sleep(delay)

		# All retries exhausted
		print(f"[REST] All retries exhausted. Returning error.")
		return jsonify({"error": "Backend failure", "details": str(last_error)}), 500

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
	# Delete specific item with retry logic and circuit breaker
	# - 3 attempts with exponential backoff (0ms, 100ms, 200ms)
	# - Circuit breaker opens after 3 consecutive failures
	# - Returns 503 when circuit is open

	item_data = request.get_json()

	if not item_data or item_data['id'] != item_id:
		return jsonify({"error": "Bad request"}), 400
	
	# Retry configuration
	max_attempts = 3
	delays = [0, 0.1, 0.2]

	last_error = None

	for attempt in range(max_attempts):
		try:
			print(f"[REST] Attempt {attempt + 1}/{max_attempts}")

			# Call gRPC through circuit breaker
			response = breaker.call(grpc_delete_item, item_data)

			print(f"[REST] Item deleted successfully: {response.id}")
			return jsonify({"message": "Item deleted", "id": response.id, "name": response.name}), 201
		
		except CircuitBreakerError:
			# Circuit i sopen - fail fast
			print(f"[REST] Circuit breaker is OPEN - failing fast")
			return jsonify({"error": "Service unavailable"}), 503

		except grpc.RpcError as e:
			last_error = e
			print(f"[REST] gRPC Error on attempt {attempt + 1}: {e.code()}")
			# Don't retry on ast attempt
			if attempt < max_attempts - 1:
				delay = delays[attempt + 1]
				print(f"[REST] Retrying in {delay}s...")
				time.sleep(delay)

	# All retries exhausted
	print(f"[REST] All retries exhausted. Returning error.")
	return jsonify({"error": "Backend failure", "details": str(last_error)}), 500

@app.route('/health', methods=['GET'])
def health():
	# Health check endpoint
	return jsonify({"status": "healthy", "circuit_breaker_state": breaker.current_state}), 200

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
