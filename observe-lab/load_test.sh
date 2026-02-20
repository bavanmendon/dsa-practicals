#!/bin/bash

echo "Generating load..."

for i in {0..100}; do
	# Create item
	curl -X POST http://localhost:5000/items -H "Content-Type: application/json" -d "{\"id\": $i, \"name\": \"Item$i\"}" &

	# Get item
	curl http://localhost:5000/items/1 &

	# List items
	curl http://localhost:5000/items &

	sleep 1
done

wait
echo "Load test complete"
