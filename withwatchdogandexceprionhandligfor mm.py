import logging
from flask import jsonify

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class UnderflowError(Exception):
    """Exception raised for underflow errors in memory operations."""
    def __init__(self, message="Attempted operation caused underflow"):
        self.message = message
        super().__init__(self.message)


def exception_handler(func):
    """
    A decorator to handle exceptions in a standardized way.
    
    :param func: The function to wrap.
    :return: Wrapped function with exception handling.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return jsonify({'error': str(e), 'message': 'An unexpected error occurred.'}), 500
    return wrapper



class MemoryManager:
    def __init__(self):
        self.memory_storage = {}
        self.buffer_memory = {}
        self.stack_memory = {}
        self.heap_memory = {}

    @exception_handler
    def allocate_memory(self, key, size):
        if key in self.memory_storage:
            raise ValueError(f"Memory already allocated for key {key}")
        self.memory_storage[key] = {'size': size, 'data': [None] * size}
        logging.info(f'Memory allocated for key {key} with size {size}')
        return f"Memory allocated for key {key} with size {size}"

    @exception_handler
    def release_memory(self, key):
        if key not in self.memory_storage:
            raise KeyError(f"No memory allocated for key {key}")
        del self.memory_storage[key]
        logging.info(f'Memory released for key {key}')
        return f"Memory released for key {key}"

    @exception_handler
    def check_memory_bounds(self, key, index):
        if key not in self.memory_storage:
            raise KeyError(f"No memory allocated for key {key}")
        if index < 0 or index >= self.memory_storage[key]['size']:
            raise IndexError(f"Index {index} is out of bounds for key {key}")
        return f"Index {index} is within bounds for key {key}"

    @exception_handler
    def resize_memory(self, key, new_size):
        if key not in self.memory_storage:
            raise KeyError(f"No memory allocated for key {key}")
        current_size = self.memory_storage[key]['size']
        self.memory_storage[key]['data'].extend([None] * (new_size - current_size))
        self.memory_storage[key]['size'] = new_size
        logging.info(f'Memory for key {key} resized from {current_size} to {new_size}')
        return f"Memory for key {key} resized from {current_size} to {new_size}"

    @exception_handler
    def create_buffer(self, key, size):
        if key in self.buffer_memory:
            raise ValueError(f"Buffer already exists for key {key}")
        self.buffer_memory[key] = {'size': size, 'data': bytearray(size)}
        logging.info(f'Buffer created for key {key} with size {size}')
        return f"Buffer created for key {key} with size {size}"

    @exception_handler
    def release_buffer(self, key):
        if key not in self.buffer_memory:
            raise KeyError(f"No buffer exists for key {key}")
        del self.buffer_memory[key]
        logging.info(f'Buffer released for key {key}')
        return f"Buffer released for key {key}"

    @exception_handler
    def get_buffer_content(self, key):
        if key not in self.buffer_memory:
            raise KeyError(f"No buffer exists for key {key}")
        return self.buffer_memory[key]['data']

    @exception_handler
    def create_stack(self, key, size):
        if key in self.stack_memory:
            raise ValueError(f"Stack already exists for key {key}")
        self.stack_memory[key] = {'size': size, 'stack': []}
        logging.info(f'Stack created for key {key} with size {size}')
        return f"Stack created for key {key} with size {size}"

    @exception_handler
    def push_stack(self, key, value):
        if key not in self.stack_memory:
            raise KeyError(f"No stack exists for key {key}")
        if len(self.stack_memory[key]['stack']) >= self.stack_memory[key]['size']:
            raise OverflowError(f"Stack overflow for key {key}")
        self.stack_memory[key]['stack'].append(value)
        logging.info(f'Value pushed to stack for key {key}')
        return f"Value pushed to stack for key {key}"

    @exception_handler
    def pop_stack(self, key):
        if key not in self.stack_memory:
            raise KeyError(f"No stack exists for key {key}")
        if not self.stack_memory[key]['stack']:
            raise UnderflowError(f"Stack underflow for key {key}")
        return self.stack_memory[key]['stack'].pop()

    @exception_handler
    def release_stack(self, key):
        if key not in self.stack_memory:
            raise KeyError(f"No stack exists for key {key}")
        del self.stack_memory[key]
        logging.info(f'Stack released for key {key}')
        return f"Stack released for key {key}"

    @exception_handler
    def allocate_heap(self, key, size):
        if key in self.heap_memory:
            raise ValueError(f"Heap memory already allocated for key {key}")
        self.heap_memory[key] = {'size': size, 'data': [None] * size}
        logging.info(f'Heap memory allocated for key {key} with size {size}')
        return f"Heap memory allocated for key {key} with size {size}"

    @exception_handler
    def release_heap(self, key):
        if key not in self.heap_memory:
            raise KeyError(f"No heap memory allocated for key {key}")
        del self.heap_memory[key]
        logging.info(f'Heap memory released for key {key}')
        return f"Heap memory released for key {key}"

    @exception_handler
    def get_heap_content(self, key):
        if key not in self.heap_memory:
            raise KeyError(f"No heap memory allocated for key {key}")
        return self.heap_memory[key]['data']

    @exception_handler
    def resize_heap(self, key, new_size):
        if key not in self.heap_memory:
            raise KeyError(f"No heap memory allocated for key {key}")
        current_size = self.heap_memory[key]['size']
        self.heap_memory[key]['data'].extend([None] * (new_size - current_size))
        self.heap_memory[key]['size'] = new_size
        logging.info(f'Heap memory for key {key} resized from {current_size} to {new_size}')
        return f"Heap memory for key {key} resized from {current_size} to {new_size}"

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
@exception_handler
def allocate_memory_endpoint():
    key = request.json.get('key')
    size = request.json.get('size')
    response = memory_manager.allocate_memory(key, size)
    return jsonify({'message': response})

@app.route('/release_memory', methods=['POST'])
@exception_handler
def release_memory_endpoint():
    key = request.json.get('key')
    response = memory_manager.release_memory(key)
    return jsonify({'message': response})

@app.route('/check_memory_bounds', methods=['POST'])
@exception_handler
def check_memory_bounds_endpoint():
    key = request.json.get('key')
    index = request.json.get('index')
    response = memory_manager.check_memory_bounds(key, index)
    return jsonify({'message': response})

@app.route('/resize_memory', methods=['POST'])
@exception_handler
def resize_memory_endpoint():
    key = request.json.get('key')
    new_size = request.json.get('new_size')
    response = memory_manager.resize_memory(key, new_size)
    return jsonify({'message': response})

# Buffer Memory Management Endpoints
@app.route('/create_buffer', methods=['POST'])
@exception_handler
def create_buffer_endpoint():
    key = request.json.get('key')
    size = request.json.get('size')
    response = memory_manager.create_buffer(key, size)
    return jsonify({'message': response})

@app.route('/release_buffer', methods=['POST'])
@exception_handler
def release_buffer_endpoint():
    key = request.json.get('key')
    response = memory_manager.release_buffer(key)
    return jsonify({'message': response})

@app.route('/get_buffer_content', methods=['POST'])
@exception_handler
def get_buffer_content_endpoint():
    key = request.json.get('key')
    response = memory_manager.get_buffer_content(key)
    return jsonify({'content': response})

# Stack Memory Management Endpoints
@app.route('/create_stack', methods=['POST'])
@exception_handler
def create_stack_endpoint():
    key = request.json.get('key')
    size = request.json.get('size')
    response = memory_manager.create_stack(key, size)
    return jsonify({'message': response})

@app.route('/push_stack', methods=['POST'])
@exception_handler
def push_stack_endpoint():
    key = request.json.get('key')
    value = request.json.get('value')
    response = memory_manager.push_stack(key, value)
    return jsonify({'message': response})

@app.route('/pop_stack', methods=['POST'])
@exception_handler
def pop_stack_endpoint():
    key = request.json.get('key')
    response = memory_manager.pop_stack(key)
    return jsonify({'message': response})

@app.route('/release_stack', methods=['POST'])
@exception_handler
def release_stack_endpoint():
    key = request.json.get('key')
    response = memory_manager.release_stack(key)
    return jsonify({'message': response})

# Heap Memory Management Endpoints
@app.route('/allocate_heap', methods=['POST'])
@exception_handler
def allocate_heap_endpoint():
    key = request.json.get('key')
    size = request.json.get('size')
    response = memory_manager.allocate_heap(key, size)
    return jsonify({'message': response})

@app.route('/release_heap', methods=['POST'])
@exception_handler
def release_heap_endpoint():
    key = request.json.get('key')
    response = memory_manager.release_heap(key)
    return jsonify({'message': response})

@app.route('/get_heap_content', methods=['POST'])
@exception_handler
def get_heap_content_endpoint():
    key = request.json.get('key')
    response = memory_manager.get_heap_content(key)
    return jsonify({'content': response})

@app.route('/resize_heap', methods=['POST'])
@exception_handler
def resize_heap_endpoint():
    key = request.json.get('key')
    new_size = request.json.get('new_size')
    response = memory_manager.resize_heap(key, new_size)
    return jsonify({'message': response})

# Endpoint for getting memory usage
@app.route('/memory_usage', methods=['GET'])
@exception_handler
def memory_usage_endpoint():
    response = memory_manager.get_memory_usage()
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
