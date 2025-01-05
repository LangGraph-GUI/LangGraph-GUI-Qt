import asyncio

class ProcessHandler:
    def __init__(self):
        self._process = None

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
                        print(f"{prefix}{line.decode().strip()}")
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
                return {"status": "success", "message": "Process completed successfully"}
            else:
                return {"status": "error", "message": f"Process exited with code {self._process.returncode}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            self._process = None

    async def status(self):
        # Simply check if process exists and hasn't completed
        return {
            "is_running": self._process is not None
        }
