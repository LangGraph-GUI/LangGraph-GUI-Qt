# ServerTee.py

import sys
import datetime
from threading import Lock
from queue import Queue, Empty

class ServerTee:
    def __init__(self, filename, mode='a'):
        self.file = open(filename, mode)
        self.stdout = sys.stdout
        self.lock = Lock()
        self.subscribers = []
        sys.stdout = self

    def write(self, message):
        with self.lock:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message_with_timestamp = f"{timestamp} - {message}"
            self.stdout.write(message_with_timestamp)
            self.stdout.flush()  # Ensure immediate output to console
            self.file.write(message_with_timestamp)
            self.file.flush()  # Ensure immediate write to file
            self.notify_subscribers(message_with_timestamp)

    def flush(self):
        with self.lock:
            self.stdout.flush()
            self.file.flush()

    def close(self):
        with self.lock:
            sys.stdout = self.stdout
            self.file.close()

    def notify_subscribers(self, message):
        for subscriber in self.subscribers:
            subscriber.put(message)

    def subscribe(self):
        q = Queue()
        self.subscribers.append(q)
        return q

    def unsubscribe(self, q):
        self.subscribers.remove(q)

    def stream_to_frontend(self):
        q = self.subscribe()
        try:
            while True:
                try:
                    message = q.get(timeout=1)
                    yield message + "\n"
                except Empty:
                    continue
        finally:
            self.unsubscribe(q)