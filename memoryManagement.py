from flask import Flask, request, jsonify

class MemoryManager:
    def __init__(self):
        self.memory_storage = {}  # General memory storage
        self.buffer_memory = {}  # Buffer memory storage
        self.stack_memory = {}  # Stack memory storage
        self.heap_memory = {}  # Heap memory storage

    # General Memory Management
    def allocate_memory(self, key, size):
        if key in self.memory_storage:
            return f"Memory already allocated for key {key}"
        self.memory_storage[key] = {'size': size, 'data': [None] * size}
        return f"Memory allocated for key {key} with size {size}"

    def release_memory(self, key):
        if key not in self.memory_storage:
            return f"No memory allocated for key {key}"
        del self.memory_storage[key]
        return f"Memory released for key {key}"

    def check_memory_bounds(self, key, index):
        if key not in self.memory_storage:
            return f"No memory allocated for key {key}"
        if index < 0 or index >= self.memory_storage[key]['size']:
            return f"Index {index} is out of bounds for key {key} with size {self.memory_storage[key]['size']}"
        return f"Index {index} is within bounds for key {key}"

    def resize_memory(self, key, new_size):
        if key not in self.memory_storage:
            return f"No memory allocated for key {key}"
        current_size = self.memory_storage[key]['size']
        self.memory_storage[key]['data'].extend([None] * (new_size - current_size))
        self.memory_storage[key]['size'] = new_size
        return f"Memory for key {key} resized from {current_size} to {new_size}"

    # Buffer Memory Management
    def create_buffer(self, key, size):
        if key in self.buffer_memory:
            return f"Buffer already exists for key {key}"
        self.buffer_memory[key] = {'size': size, 'data': bytearray(size)}
        return f"Buffer created for key {key} with size {size}"

    def release_buffer(self, key):
        if key not in self.buffer_memory:
            return f"No buffer exists for key {key}"
        del self.buffer_memory[key]
        return f"Buffer released for key {key}"

    def get_buffer_content(self, key):
        if key not in self.buffer_memory:
            return f"No buffer exists for key {key}"
        return self.buffer_memory[key]['data']

    # Stack Memory Management
    def create_stack(self, key, size):
        if key in self.stack_memory:
            return f"Stack already exists for key {key}"
        self.stack_memory[key] = {'size': size, 'stack': []}
        return f"Stack created for key {key} with size {size}"

    def push_stack(self, key, value):
        if key not in self.stack_memory:
            return f"No stack exists for key {key}"
        if len(self.stack_memory[key]['stack']) >= self.stack_memory[key]['size']:
            return f"Stack overflow for key {key}"
        self.stack_memory[key]['stack'].append(value)
        return f"Value pushed to stack for key {key}"

    def pop_stack(self, key):
        if key not in self.stack_memory:
            return f"No stack exists for key {key}"
        if not self.stack_memory[key]['stack']:
            return f"Stack underflow for key {key}"
        return self.stack_memory[key]['stack'].pop()

    def release_stack(self, key):
        if key not in self.stack_memory:
            return f"No stack exists for key {key}"
        del self.stack_memory[key]
        return f"Stack released for key {key}"

    # Heap Memory Management
    def allocate_heap(self, key, size):
        if key in self.heap_memory:
            return f"Heap memory already allocated for key {key}"
        self.heap_memory[key] = {'size': size, 'data': [None] * size}
        return f"Heap memory allocated for key {key} with size {size}"

    def release_heap(self, key):
        if key not in self.heap_memory:
            return f"No heap memory allocated for key {key}"
        del self.heap_memory[key]
        return f"Heap memory released for key {key}"

    def get_heap_content(self, key):
        if key not in self.heap_memory:
            return f"No heap memory allocated for key {key}"
        return self.heap_memory[key]['data']

    def resize_heap(self, key, new_size):
        if key not in self.heap_memory:
            return f"No heap memory allocated for key {key}"
        current_size = self.heap_memory[key]['size']
        self.heap_memory[key]['data'].extend([None] * (new_size - current_size))
        self.heap_memory[key]['size'] = new_size
        return f"Heap memory for key {key} resized from {current_size} to {new_size}"

    # Get memory usage summary
    def get_memory_usage(self):
        return {
            'general_memory': {key: len(value['data']) for key, value in self.memory_storage.items()},
            'buffer_memory': {key: len(value['data']) for key, value in self.buffer_memory.items()},
            'stack_memory': {key: len(value['stack']) for key, value in self.stack_memory.items()},
            'heap_memory': {key: len(value['data']) for key, value in self.heap_memory.items()}
        }


from flask import Flask, request, jsonify

app = Flask(__name__)
memory_manager = MemoryManager()

# General Memory Management Endpoints
@app.route('/allocate_memory', methods=['POST'])
def allocate_memory_endpoint():
    key = request.json.get('key')
    size = request.json.get('size')
    response = memory_manager.allocate_memory(key, size)
    return jsonify({'message': response})

@app.route('/release_memory', methods=['POST'])
def release_memory_endpoint():
    key = request.json.get('key')
    response = memory_manager.release_memory(key)
    return jsonify({'message': response})

@app.route('/check_memory_bounds', methods=['POST'])
def check_memory_bounds_endpoint():
    key = request.json.get('key')
    index = request.json.get('index')
    response = memory_manager.check_memory_bounds(key, index)
    return jsonify({'message': response})

@app.route('/resize_memory', methods=['POST'])
def resize_memory_endpoint():
    key = request.json.get('key')
    new_size = request.json.get('new_size')
    response = memory_manager.resize_memory(key, new_size)
    return jsonify({'message': response})

# Buffer Memory Management Endpoints
@app.route('/create_buffer', methods=['POST'])
def create_buffer_endpoint():
    key = request.json.get('key')
    size = request.json.get('size')
    response = memory_manager.create_buffer(key, size)
    return jsonify({'message': response})

@app.route('/release_buffer', methods=['POST'])
def release_buffer_endpoint():
    key = request.json.get('key')
    response = memory_manager.release_buffer(key)
    return jsonify({'message': response})

@app.route('/get_buffer_content', methods=['POST'])
def get_buffer_content_endpoint():
    key = request.json.get('key')
    response = memory_manager.get_buffer_content(key)
    return jsonify({'content': response})

# Stack Memory Management Endpoints
@app.route('/create_stack', methods=['POST'])
def create_stack_endpoint():
    key = request.json.get('key')
    size = request.json.get('size')
    response = memory_manager.create_stack(key, size)
    return jsonify({'message': response})

@app.route('/push_stack', methods=['POST'])
def push_stack_endpoint():
    key = request.json.get('key')
    value = request.json.get('value')
    response = memory_manager.push_stack(key, value)
    return jsonify({'message': response})

@app.route('/pop_stack', methods=['POST'])
def pop_stack_endpoint():
    key = request.json.get('key')
    response = memory_manager.pop_stack(key)
    return jsonify({'message': response})

@app.route('/release_stack', methods=['POST'])
def release_stack_endpoint():
    key = request.json.get('key')
    response = memory_manager.release_stack(key)
    return jsonify({'message': response})

# Heap Memory Management Endpoints
@app.route('/allocate_heap', methods=['POST'])
def allocate_heap_endpoint():
    key = request.json.get('key')
    size = request.json.get('size')
    response = memory_manager.allocate_heap(key, size)
    return jsonify({'message': response})

@app.route('/release_heap', methods=['POST'])
def release_heap_endpoint():
    key = request.json.get('key')
    response = memory_manager.release_heap(key)
    return jsonify({'message': response})

@app.route('/get_heap_content', methods=['POST'])
def get_heap_content_endpoint():
    key = request.json.get('key')
    response = memory_manager.get_heap_content(key)
    return jsonify({'content': response})

@app.route('/resize_heap', methods=['POST'])
def resize_heap_endpoint():
    key = request.json.get('key')
    new_size = request.json.get('new_size')
    response = memory_manager.resize_heap(key, new_size)
    return jsonify({'message': response})

# Endpoint for getting memory usage
@app.route('/memory_usage', methods=['GET'])
def memory_usage_endpoint():
    response = memory_manager.get_memory_usage()
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
