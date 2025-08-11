import asyncio
import json
import uvicorn
import os
from dotenv import load_dotenv
import requests
from mcp import types as mcp_types 
from mcp.server.lowlevel import Server

from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route


from google.adk.tools.function_tool import FunctionTool


from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type


load_dotenv()
APP_HOST = os.environ.get("APP_HOST", "0.0.0.0")
APP_PORT = os.environ.get("APP_PORT",8080)
API_SERVER_URL = os.environ.get('API_SERVER_URL')

app = Server("Nexus-of-Whispers")
sse = SseServerTransport("/messages/")

#REPLACE-MAGIC-CORE


cryosea_shatterTool = FunctionTool(cryosea_shatter)
moonlit_cascadeTool = FunctionTool(moonlit_cascade)

available_tools = {
    cryosea_shatterTool.name: cryosea_shatterTool,
    moonlit_cascadeTool.name: moonlit_cascadeTool,
}


#REPLACE-Runes of Communication

# Create a named MCP Server instance

# --- MCP Remote Server ---
async def handle_sse(request):
  """Runs the MCP server over standard input/output."""
  # Use the stdio_server context manager from the MCP library
  async with sse.connect_sse(
    request.scope, request.receive, request._send
  ) as streams:
    await app.run(
        streams[0], streams[1], app.create_initialization_options()
    )

starlette_app = Starlette(
 debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
  print("Launching MCP Server exposing ADK tools...")
  try:
    asyncio.run(uvicorn.run(starlette_app, host=APP_HOST, port=APP_PORT))
  except KeyboardInterrupt:
    print("\nMCP Server stopped by user.")
  except Exception as e:
    print(f"MCP Server encountered an error: {e}")
  finally:
    print("MCP Server process exiting.")
# --- End MCP Server ---



