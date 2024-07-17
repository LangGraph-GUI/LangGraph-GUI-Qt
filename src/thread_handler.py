# thread_handler.py

import threading
import ctypes

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

    def start_thread(self, target):
        with self.lock:
            if self.current_thread and self.current_thread.is_alive():
                raise Exception("Another instance is already running")
            self.current_thread = threading.Thread(target=self._wrap_target(target))
            self.current_thread.start()

    def _wrap_target(self, target):
        def wrapper():
            try:
                target()
            except Exception as e:
                print(f"Thread crashed: {e}")
            finally:
                with self.lock:
                    self.current_thread = None
        return wrapper

    def stop_thread(self):
        with self.lock:
            if self.current_thread and self.current_thread.is_alive():
                self._terminate_thread(self.current_thread)
                self.current_thread.join()
            self.current_thread = None

    def _terminate_thread(self, thread):
        if not thread.is_alive():
            return
        exc = ctypes.py_object(SystemExit)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread.ident), exc)
        if res == 0:
            raise ValueError("Invalid thread ID")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def force_reset(self):
        with self.lock:
            if self.current_thread and self.current_thread.is_alive():
                self._terminate_thread(self.current_thread)
                self.current_thread.join()
            self.current_thread = None

    def is_running(self):
        with self.lock:
            return self.current_thread is not None and self.current_thread.is_alive()
