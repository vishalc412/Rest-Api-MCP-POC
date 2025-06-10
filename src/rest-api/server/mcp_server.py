#!/usr/bin/env python3
import json
import logging
import sys
import os
from typing import Optional
import aiohttp
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import asyncio

# Add the current directory to Python path to find models.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

server = Server("user-api")

API_BASE_URL = "http://localhost:8000"

# Configure logging to stderr to avoid stdio conflicts
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)

async def api_call(method: str, endpoint: str, data: Optional[dict] = None) -> dict:
    """Make API calls to the FastAPI server"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{API_BASE_URL}{endpoint}"
            kwargs = {"json": data} if data else {}
            
            logger.debug(f"Making {method} request to {url} with data: {data}")
            
            async with session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                logger.debug(f"API response status: {response.status}, body: {response_text}")
                
                if response.status not in [200, 201]:
                    raise Exception(f"API call failed with status {response.status}: {response_text}")
                
                return json.loads(response_text) if response_text else {}
    except Exception as e:
        logger.error(f"API call error: {str(e)}")
        raise

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all tools available in the API."""
    logger.info("Listing tools")
    return [
        types.Tool(
            name="create_user",
            description="Create a new user with name, email, and optional age",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string", 
                        "description": "Name of the user",
                        "minLength": 3,
                        "maxLength": 100
                    },
                    "email": {
                        "type": "string", 
                        "description": "Email of the user",
                        "format": "email"
                    },
                    "age": {
                        "type": "integer", 
                        "description": "Age of the user", 
                        "minimum": 18, 
                        "maximum": 100
                    }
                },
                "required": ["name", "email"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="get_user",
            description="Get a user by their ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string", 
                        "description": "ID of the user to retrieve"
                    }
                },
                "required": ["user_id"],
                "additionalProperties": False
            }
        ),
        types.Tool(
            name="list_users",
            description="List all users with optional pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "skip": {
                        "type": "integer", 
                        "description": "Number of users to skip for pagination", 
                        "default": 0,
                        "minimum": 0
                    },
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of users to return", 
                        "default": 100,
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    
    if arguments is None:
        arguments = {}
    
    try:
        if name == "create_user":
            result = await api_call("POST", "/users", data=arguments)
            return [types.TextContent(
                type="text", 
                text=f"✅ User created successfully:\n```json\n{json.dumps(result, indent=2)}\n```"
            )]
            
        elif name == "get_user":
            user_id = arguments.get("user_id")
            if not user_id:
                raise ValueError("user_id is required")
            
            result = await api_call("GET", f"/users/{user_id}")
            return [types.TextContent(
                type="text", 
                text=f"👤 User details:\n```json\n{json.dumps(result, indent=2)}\n```"
            )]
            
        elif name == "list_users":
            skip = arguments.get("skip", 0)
            limit = arguments.get("limit", 100)
            result = await api_call("GET", f"/users?skip={skip}&limit={limit}")
            
            if isinstance(result, list):
                count = len(result)
                return [types.TextContent(
                    type="text", 
                    text=f"📋 Found {count} users:\n```json\n{json.dumps(result, indent=2)}\n```"
                )]
            else:
                return [types.TextContent(
                    type="text", 
                    text=f"📋 Users data:\n```json\n{json.dumps(result, indent=2)}\n```"
                )]
        else:
            raise ValueError(f"Unknown tool name: {name}")
            
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return [types.TextContent(
            type="text", 
            text=f"❌ Error executing {name}: {str(e)}"
        )]

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List all resources available in the API."""
    logger.info("Listing resources")
    return [
        types.Resource(
            uri="user-api://stats",
            name="User Statistics",
            description="Statistics and analytics about the user database",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a resource by URI."""
    logger.info(f"Reading resource: {uri}")
    
    if uri == "user-api://stats":
        try:
            users = await api_call("GET", "/users?limit=1000")
            
            if not isinstance(users, list):
                users = []
            
            total_users = len(users)
            ages = [user.get("age") for user in users if user.get("age") is not None]
            average_age = sum(ages) / len(ages) if ages else 0
            
            stats = {
                "total_users": total_users,
                "average_age": round(average_age, 2),
                "users_with_age": len(ages),
                "age_distribution": {
                    "18-30": len([age for age in ages if 18 <= age <= 30]),
                    "31-50": len([age for age in ages if 31 <= age <= 50]),
                    "51+": len([age for age in ages if age > 50])
                } if ages else {},
                "sample_emails": [user["email"] for user in users[:5]] if users else []
            }
            return json.dumps(stats, indent=2)
        except Exception as e:
            logger.error(f"Error reading stats: {str(e)}")
            return json.dumps({"error": f"Failed to fetch stats: {str(e)}"}, indent=2)
    else:
        raise ValueError(f"Unknown resource URI: {uri}")

async def run():
    """Main server run function"""
    try:
        logger.info("Starting user-api MCP server...")
        
        # Initialize the server with proper options
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="user-api",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                )
            )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

def main():
    """Entry point"""
    try:
        logger.info("Initializing MCP server...")
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()