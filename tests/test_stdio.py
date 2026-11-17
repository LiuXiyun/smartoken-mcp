import os
import sys
import unittest
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).resolve().parents[1] / 'smartoken_mcp.py'

class StdioTests(unittest.IsolatedAsyncioTestCase):
    async def test_tools_and_missing_key_error_close_cleanly(self):
        parameters = StdioServerParameters(
            command=sys.executable,
            args=[str(SERVER)],
            env={'SMTOKEN_API_KEY': '', 'PATH': os.environ.get('PATH', '')},
        )
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                self.assertEqual({tool.name for tool in tools.tools}, {'list_models', 'chat_completion'})
                result = await session.call_tool('chat_completion', {'model': 'deepseek-v4.1-flash', 'prompt': 'test', 'max_tokens': 10})
                self.assertTrue(result.isError)
                self.assertIn('SMTOKEN_API_KEY', result.content[0].text)

if __name__ == '__main__':
    unittest.main()
