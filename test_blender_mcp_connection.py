import socket
import subprocess
import sys
import time
from pathlib import Path

workspace = Path(__file__).resolve().parent
blender = r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
python = r'C:\Users\ASUS\AppData\Roaming\uv\tools\blender-mcp\Scripts\python.exe'
log_path = workspace / 'blender-mcp-verification.log'
with log_path.open('w', encoding='utf-8') as log:
    process = subprocess.Popen(
        [blender, '--background', '--command', 'blender_mcp', '--host', '127.0.0.1', '--port', '9876'],
        stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW,
    )
    try:
        deadline = time.monotonic() + 25
        while True:
            if process.poll() is not None:
                raise RuntimeError(f'Blender exited with code {process.returncode}')
            try:
                with socket.create_connection(('127.0.0.1', 9876), timeout=1):
                    break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError('Blender MCP bridge did not start')
                time.sleep(0.25)
        result = subprocess.run(
            [python, str(workspace / 'verify_blender_mcp.py'), '--live'],
            timeout=55, creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, text=True,
        )
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        if result.returncode:
            raise RuntimeError(f'MCP verification failed: {result.returncode}')
        print('PASS: MCP startup, tool discovery, and live Blender scene read.')
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
print('Temporary verification instance stopped.')

