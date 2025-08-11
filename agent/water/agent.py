import asyncio
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
import logging 
import nest_asyncio 
from toolbox_core import ToolboxSyncClient



load_dotenv()
# Load environment variables from .env file in the parent directory
# Place this near the top, before using env vars like API keys

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
 
# --- Global variables ---
# Define them first, initialize as None
root_agent: LlmAgent | None = None
exit_stack: AsyncExitStack | None = None


API_TOOLS_URL = os.environ.get("API_TOOLS_URL")
FUNCTION_TOOLS_URL = os.environ.get("FUNCTION_TOOLS_URL")
PUBLIC_URL = os.environ.get("PUBLIC_URL")

print(f"API_TOOLS_URL: {API_TOOLS_URL}")
print(f"FUNCTION_TOOLS_URL: {FUNCTION_TOOLS_URL}")
print(f"PUBLIC_URL: {PUBLIC_URL}")
 

#REPLACE-setup-MCP

#REPLACE-worker-agents

#REPLACE-parallel-agent

#REPLACE - add A2A