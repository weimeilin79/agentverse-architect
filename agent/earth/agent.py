import asyncio
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.loop_agent import LoopAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
import logging 
import nest_asyncio 
from typing import Optional
from google.genai import types
import requests
from datetime import datetime, timezone, timedelta
from toolbox_core import ToolboxSyncClient
from google.adk.agents.callback_context import CallbackContext




load_dotenv()

COOLDOWN_PERIOD_SECONDS = 60
COOLDOWN_API_URL = os.environ.get("API_SERVER_URL")
print(f"COOLDOWN_API_URL: {COOLDOWN_API_URL}")



logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
 
# --- Global variables ---
# Define them first, initialize as None
root_agent: LlmAgent | None = None
exit_stack: AsyncExitStack | None = None


FUNCTION_TOOLS_URL = os.environ.get("FUNCTION_TOOLS_URL")
PUBLIC_URL = os.environ.get("PUBLIC_URL")


print(f"FUNCTION_TOOLS_URL: {FUNCTION_TOOLS_URL}")
print(f"PUBLIC_URL: {PUBLIC_URL}")


#REPLACE-before_agent-function

#REPLACE-setup-MCP

#REPLACE-worker-agents

#REPLACE-loop-agent

#REPLACE - add A2A