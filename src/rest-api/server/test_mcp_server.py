#!/usr/bin/env python3
import asyncio
import sys
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types

# Create minimal server
server = Server("test-mcp")

@server.list_tools()
async def handle_list_tools():
    return [
        types.Tool(
            name="test_hello",
            description="Simple test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "test_hello":
        return [
            types.TextContent(
                type="text",
                text=f"Hello, {arguments.get('name', 'World')}!"
            )
        ]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    # Use stderr for logging to avoid interfering with stdio protocol
    print("Starting test MCP server...", file=sys.stderr)
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            {
                "server_name": "test-mcp",
                "server_version": "1.0.0"
            }
        )

if __name__ == "__main__":
    asyncio.run(main())