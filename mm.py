import traceback
import gc
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

@staticmethod
def generic_try_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {str(e)}")
            traceback.print_exc()
    return wrapper

class MemoryManagementService:
    @staticmethod
    @generic_try_except
    def garbage_collection():
        try:
            # Perform garbage collection
            gc.collect()
            print("Garbage collection executed successfully.")
        except Exception as e:
            print("Error in garbage collection:")
            traceback.print_exc()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def on_modified(self, event):
        if event.src_path.endswith("sample1.txt"):  # Check if the modified file is "sample1.txt"
            print("Detected modification in sample1.txt. Triggering garbage collection.")
            self.memory_manager.garbage_collection()

# Example usage with watchdog:
if __name__ == "__main__":
    memory_manager = MemoryManagementService()
    
    observer = Observer()
    event_handler = FileChangeHandler(memory_manager)
    directory_to_watch = "."  # Update with the correct directory path
    observer.schedule(event_handler, path=directory_to_watch, recursive=False)

    try:
        observer.start()
        print(f"Watching for changes in {directory_to_watch}...")
        observer.join()  # Keep the observer running
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
