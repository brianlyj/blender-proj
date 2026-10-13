import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    env = os.environ.copy()
    env.update({
        'BLENDER_PATH': r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',
        'BLENDER_MCP_HOST': '127.0.0.1',
        'BLENDER_MCP_PORT': '9876',
    })
    params = StdioServerParameters(
        command=r'C:\Users\ASUS\.local\bin\blender-mcp.exe',
        args=['--transport', 'stdio'],
        env=env,
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            tools = await session.list_tools()
            names = [tool.name for tool in tools.tools]
            assert 'get_objects_summary' in names
            assert 'execute_blender_code' in names
            print(json.dumps({'server': init.serverInfo.model_dump(), 'tool_count': len(names), 'tools': names}, indent=2))
            if '--live' in sys.argv:
                result = await session.call_tool('get_objects_summary', {})
                print(result.model_dump_json(indent=2))
                assert not result.isError, 'Live Blender connection failed'

asyncio.run(asyncio.wait_for(main(), timeout=45))
