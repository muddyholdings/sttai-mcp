"""Smoke test: the server module imports, registers tools, and speaks MCP
over stdio without an API key set."""
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_tools_registered():
    from sttai_mcp.server import mcp
    names = {t.name for t in asyncio.run(mcp.list_tools())}
    assert {"list_transcripts", "get_transcript"} <= names


def test_server_starts_over_stdio():
    env = {k: v for k, v in os.environ.items() if k != "STT_API_KEY"}
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "sttai_mcp.server"], env=env)

    async def run():
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await asyncio.wait_for(s.initialize(), 30)
                return await asyncio.wait_for(s.list_tools(), 30)

    assert len(asyncio.run(run()).tools) > 5
