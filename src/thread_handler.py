# thread_handler.py

import threading

class ThreadHandler:
    _instance = None

    @staticmethod
    def get_instance():
        if ThreadHandler._instance is None:
            ThreadHandler()
        return ThreadHandler._instance

    def __init__(self):
        if ThreadHandler._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ThreadHandler._instance = self
            self.lock = threading.Lock()
            self.current_thread = None
            self.stop_event = threading.Event()

    def start_thread(self, target):
        with self.lock:
            if self.current_thread and self.current_thread.is_alive():
                raise Exception("Another instance is already running")
            self.stop_event.clear()
            self.current_thread = threading.Thread(target=target)
            self.current_thread.start()

    def stop_thread(self):
        with self.lock:
            if self.current_thread and self.current_thread.is_alive():
                self.stop_event.set()
                self.current_thread.join()
            self.current_thread = None

    def force_reset(self):
        with self.lock:
            if self.current_thread and self.current_thread.is_alive():
                self.stop_event.set()
                self.current_thread.join()
            self.current_thread = None
            self.stop_event.clear()

    def is_running(self):
        with self.lock:
            return self.current_thread is not None and self.current_thread.is_alive()
