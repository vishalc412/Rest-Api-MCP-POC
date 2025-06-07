import json
from typing import Optional
import aiohttp
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import asyncio

server = Server("user-api-mcp")

API_BASE_URL = "http://localhost:8000"

async def api_call(method: str, endpoint: str, data: Optional[dict] = None) -> dict:
    async with aiohttp.ClientSession() as session:
        url = f"{API_BASE_URL}{endpoint}"
        kwargs = {"json":data} if data else {}

        async with session.request(method, url, **kwargs) as response:
            if response.status != 200:
                raise Exception(f"API call failed with status {response.status}")
            return await response.json()

    
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all tools available in the API."""
    return [
        types.Tool(
            name="Create User",
            description="Create a new user",
            inputSchema={
                "type": "object",
                "properties":{
                    "name": {"type": "string", "description": "Name of the user"},
                    "email": {"type": "string", "description": "Email of the user"},
                    "age": {"type": "integer", "description": "Age of the user", "minimum": 0, "maximum": 100}
                },
                "required": ["name","email"]
            }
        ),
        types.Tool(
            name="Get User",
            description="Get a user by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "ID of the user"}
                },
                "required": ["user_id"]
            }
        ),
        types.Tool(
            name="List Users",
            description="List all users",
            inputSchema={
                "type": "object",
                "properties": {
                    "skip": {"type": "integer", "description": "Number of users to skip", "default": 0},
                    "limit": {"type": "integer", "description": "Maximum number of users to return", "default": 100}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool( name: str, arguments: dict | None)-> list[types.TextContent|types.ImageContent|types.EmbeddedResource]:
    try:
        if name =="create_user":
            result = await api_call("POST", "/users", data=arguments)
            return [types.TextContent(type="text",text=f"User created:\n{json.dumps(result,indent=2)}")]
        elif name == "get_user":
            user_id = arguments.get("user_id")
            if not user_id:
                raise ValueError("user_id is required")
            result = await api_call("GET", f"/user/{user_id}")
            return [types.TextContent(type="text", text=f"User details:\n{json.dumps(result, indent=2)}")]
        elif name == "list_users":
            skip = arguments.get("skip", 0)
            limit = arguments.get("limit", 100)
            result = await api_call("GET", f"/user?skip={skip}&limit={limit}")
            return [types.TextContent(type="text", text=f"Users:\n{json.dumps(result, indent=2)}")]
        else:
            raise ValueError(f"Unknown tool name: {name}")
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List all resources available in the API."""
    return [
        types.Resource(
            uri = "user-api://stats",
            name = "User Stats",
            description = "Statistics about the user API",
            mimeType= "application/json"
        )
    ]

@server.read_resource()
async def handle_read_resources(uri: str) -> str:
    """Read a resource by URI."""
    if uri == "user-api://stats":
        users = await api_call("GET", "/users?limit=1000")

        stats ={
            "total_users": len(users),
            "average_age": sum(user.get("age", 0) for user in users) / len(users) if users else 0,
            "user_emails": [user["email"] for user in users]
        }
        return json.dumps(stats, indent=2)
    return ValueError(f"Unknown resource URI: {uri}")

async def run():
    async with mcp.server.stdio.stdio_Server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="user-api-mcp",
                server_version="1.0.0",
                capabilities= server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )
if __name__ == "__main__":
    asyncio.run(run())
        