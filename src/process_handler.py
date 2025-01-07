# process_handler.py

import asyncio
from asyncio import Queue as AsyncQueue
import sys

class ProcessHandler:
    def __init__(self):
        self._process = None
        self._output_queue = AsyncQueue()  # Use asyncio.Queue
        self._is_running = False
        self._is_starting = False
        self._stream_tasks = []  # Store stream tasks

    async def run(self, command: list, cwd: str):
        if self._is_running or self._is_starting:
            await self._output_queue.put({"status": "error", "message": "Process already running"})
            return
        try:
            self._is_starting = True
            # clear the queue before run
            while not self._output_queue.empty():
               self._output_queue.get_nowait()

            self._process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            self._is_running = True
            self._is_starting = False

            async def stream_output(stream, prefix):
                 while True:
                     line = await stream.readline()
                     if line:
                         message = f"{prefix}{line.decode().strip()}"
                         print(message,flush=True) #flush output immediately
                         if prefix == "STDOUT: ": # only add stdout
                            await self._output_queue.put(message)
                            
                     else:
                         break

            # Create tasks and store them to cancel later
            stdout_task = asyncio.create_task(stream_output(self._process.stdout, "STDOUT: "))
            stderr_task = asyncio.create_task(stream_output(self._process.stderr, "STDERR: "))
            self._stream_tasks = [stdout_task, stderr_task]
            
            # Don't wait, let tasks run
            await self._process.wait()

            if self._process.returncode == 0:
                 await self._output_queue.put({"status": "success", "message": "Process completed successfully"})
            else:
                await self._output_queue.put({"status": "error", "message": f"Process exited with code {self._process.returncode}"})
        except Exception as e:
            await self._output_queue.put({"status": "error", "message": str(e)})
        finally:
             # Cancel the tasks and wait for cancellation to complete
             for task in self._stream_tasks:
                task.cancel()
             try:
                 await asyncio.gather(*self._stream_tasks, return_exceptions=True) # allow exception
             except asyncio.CancelledError:
                 pass

             self._stream_tasks = []
             self._is_starting = False
             self._process = None
             self._is_running = False
    async def status(self):
        return {
            "is_running": (self._is_running or self._is_starting) and self._process is not None,
        }

    def subscribe(self):
        return self._output_queue  # return the queue for external subscription

    async def get_stream(self):
      while True:
            try:
                output = await asyncio.wait_for(self._output_queue.get(),timeout=0.1)
                yield output
            except asyncio.TimeoutError:
               if not self._is_running and self._process is None:
                    break #close if process is not running
               continue