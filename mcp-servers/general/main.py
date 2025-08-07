import asyncio
import json
import uvicorn
import os
from dotenv import load_dotenv

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



def inferno_resonance(base_fire_damage: int) -> str:
    """
    Inferno Resonance
    Applies a resonance enchantment that amplifies ambient fire energy,
    multiplying the power of a fire spell by a factor of 3.
    """
    final_damage = base_fire_damage * 3
    # Thematic success message for multiplication
    return f"The Forge roars to life! The fire spell's power is multiplied by Inferno Resonance, now charged to deal {final_damage} damage."


def leviathan_surge(base_water_damage: int) -> str:
    """
    Leviathan Surge
    Channels a surge of raw water magic through the Forge,
    multiplying the power of a water-based attack by a factor of 2.
    """
    # FIX: The original code used 'base_water_damage * 3'. This now matches that logic.
    final_damage = base_water_damage * 3
    # FIX: The original f-string was broken. This is the corrected version.
    return f"A torrent of power surges from the Forge! The water spell is magnified, now ready to strike for {final_damage} damage."


def seismic_charge(current_energy: int) -> str:
    """
    Seismic Charge
    Draws raw power from the earth itself, slowly accumulating seismic energy.
    This action increments the current energy charge by 2 units.
    """
    charged_energy = current_energy + 2
    # Thematic success message for accumulation
    return f"The ground trembles as seismic energy is absorbed. The power charge has accumulated to {charged_energy} units."

inferno_resonanceTool = FunctionTool(inferno_resonance)
leviathan_surgeTool = FunctionTool(leviathan_surge)
seismic_chargeTool = FunctionTool(seismic_charge)

available_tools = {
    inferno_resonanceTool.name: inferno_resonanceTool,
    leviathan_surgeTool.name: leviathan_surgeTool,
    seismic_chargeTool.name: seismic_chargeTool,
}

# Create a named MCP Server instance
app = Server("Arcane-Forge")
sse = SseServerTransport("/messages/")

@app.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
  """MCP handler to list available tools."""
  # Convert the ADK tool's definition to MCP format
  schema_inferno_resonance = adk_to_mcp_tool_type(inferno_resonanceTool)
  schema_leviathan_surge = adk_to_mcp_tool_type(leviathan_surgeTool)
  schema_seismic_charge = adk_to_mcp_tool_type(seismic_chargeTool)
  print(f"MCP Server: Received list_tools request. \n MCP Server: Advertising tool: {schema_inferno_resonance.name},{schema_leviathan_surge.name} and {schema_seismic_charge.name}")
  return [schema_inferno_resonance,schema_leviathan_surge,schema_seismic_charge]

@app.call_tool()
async def call_tool(
    name: str, arguments: dict
) -> list[mcp_types.TextContent | mcp_types.ImageContent | mcp_types.EmbeddedResource]:
  """MCP handler to execute a tool call."""
  print(f"MCP Server: Received call_tool request for '{name}' with args: {arguments}")

  # Look up the tool by name in our dictionary
  tool_to_call = available_tools.get(name)
  if tool_to_call:
    try:
      adk_response = await tool_to_call.run_async(
          args=arguments,
          tool_context=None, # No ADK context available here
      )
      print(f"MCP Server: ADK tool '{name}' executed successfully.")
      
      response_text = json.dumps(adk_response, indent=2)
      return [mcp_types.TextContent(type="text", text=response_text)]

    except Exception as e:
      print(f"MCP Server: Error executing ADK tool '{name}': {e}")
      # Creating a proper MCP error response might be more robust
      error_text = json.dumps({"error": f"Failed to execute tool '{name}': {str(e)}"})
      return [mcp_types.TextContent(type="text", text=error_text)]
  else:
      # Handle calls to unknown tools
      print(f"MCP Server: Tool '{name}' not found.")
      error_text = json.dumps({"error": f"Tool '{name}' not implemented."})
      return [mcp_types.TextContent(type="text", text=error_text)]

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


