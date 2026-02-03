from flask import Flask, request, jsonify
app = Flask(__name__)

# In-memory storage
items = []
next_id = 1

@app.route('/items', methods=['GET'])
def get_items():
	return jsonify(items), 200

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
	item = next((i for i in items if i['id'] == item_id), None)
	if item:
		return jsonify(item), 200
	return jsonify({'error': 'Item not found'}), 404

@app.route('/items', methods=['POST'])
def create_item():
	global next_id
	data = request.get_json()
	if not data or 'name' not in data:
		return jsonify({'error': 'Bad request'}), 400
	new_item = {'id': next_id, 'name': data['name']}
	items.append(new_item)
	next_id += 1
	return jsonify(new_item), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
	item = next((i for i in items if i['id'] == item_id), None)
	if not item:
		return jsonify({'error': 'Item not found'}), 404
	data = request.get_json()
	if not data or 'name' not in data:
		return jsonify({'error': 'Bad request'}), 400
	item['name'] = data['name']
	return jsonify(item), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
	global items
	global next_id
	item = next((i for i in items if i['id'] == item_id), None)
	if not item:
		return jsonify({'error': 'Item not found'}), 404
	items = [i for i in items if i['id'] != item_id]
	items = [{'id': i['id'] - 1 if i['id'] > item_id else i['id'], 'name': i['name']} for i in items]
	next_id -= 1
	return jsonify({'message': 'Item deleted'}), 200

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
