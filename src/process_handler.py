# process_handler.py

import asyncio
from queue import Queue

class ProcessHandler:
    def __init__(self):
        self._process = None
        self._output_queue = Queue()  # Queue to send output to subscribers

    async def run(self, command: list, cwd: str):
        # If a process is already running, return an error
        if self._process is not None:
            return {"status": "error", "message": "Process already running"}
        
        try:
            self._process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Stream output to parent process in real-time
            async def stream_output(stream, prefix):
                while True:
                    line = await stream.readline()
                    if line:
                        message = f"{prefix}{line.decode().strip()}"
                        print(message)
                        if prefix == "STDOUT: ": #only add stdout
                           self._output_queue.put(message)
                    else:
                        break

            # Create tasks to stream both stdout and stderr
            stdout_task = asyncio.create_task(stream_output(self._process.stdout, "STDOUT: "))
            stderr_task = asyncio.create_task(stream_output(self._process.stderr, "STDERR: "))

            # Wait for the process to complete
            await self._process.wait()
            await asyncio.gather(stdout_task, stderr_task)
            
            # Return final status
            if self._process.returncode == 0:
                 self._output_queue.put({"status": "success", "message": "Process completed successfully"})
                 return 
            else:
                self._output_queue.put({"status": "error", "message": f"Process exited with code {self._process.returncode}"})
                return 
        except Exception as e:
            self._output_queue.put({"status": "error", "message": str(e)})
            return
        finally:
            self._process = None

    async def status(self):
        # Simply check if process exists and hasn't completed
        return {
            "is_running": self._process is not None
        }

    def subscribe(self):
        return self._output_queue  # return the queue for external subscription
    
    def get_stream(self):
         while True:
             try:
                output = self._output_queue.get(timeout=0.1)
                yield output
             except Exception as e:
                 if self._process is None: # to close stream
                   break
                 continue