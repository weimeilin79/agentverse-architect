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


def check_cool_down(callback_context: CallbackContext) -> Optional[types.Content]:
    """
    This callback checks an external API to see if the agent is on cooldown.
    If it is, it terminates the run by returning a message.
    If it's not, it updates the cooldown timestamp and allows the run to proceed by returning None.
    """
    agent_name = callback_context.agent_name
    print(f"[Callback] Before '{agent_name}': Checking cooldown status...")

    # --- 1. CHECK the Cooldown API ---
    try:
        response = requests.get(f"{COOLDOWN_API_URL}/cooldown/{agent_name}")
        response.raise_for_status()
        data = response.json()
        last_used_str = data.get("time")
    except requests.exceptions.RequestException as e:
        print(f"[Callback] ERROR: Could not reach Cooldown API. Allowing agent to run. Reason: {e}")
        return None # Fail open: if the API is down, let the agent work.

    # --- 2. EVALUATE the Cooldown Status ---
    if last_used_str:
        last_used_time = datetime.fromisoformat(last_used_str)
        time_since_last_use = datetime.now(timezone.utc) - last_used_time

        if time_since_last_use < timedelta(seconds=COOLDOWN_PERIOD_SECONDS):
            # AGENT IS ON COOLDOWN. Terminate the run.
            seconds_remaining = int(COOLDOWN_PERIOD_SECONDS - time_since_last_use.total_seconds())
            override_message = (
                f"The {agent_name} is exhausted and must recover its power. "
                f"It cannot be summoned for another {seconds_remaining} seconds."
            )
            print(f"[Callback] Cooldown active for '{agent_name}'. Terminating with message.")
            # Returning a Content object stops the agent and sends this message to the user.
            return types.Content(parts=[types.Part(text=override_message)])

    # --- 3. UPDATE the Cooldown API (if not on cooldown) ---
    current_time_iso = datetime.now(timezone.utc).isoformat()
    payload = {"timestamp": current_time_iso}
    
    print(f"[Callback] '{agent_name}' is available. Updating timestamp via Cooldown API...")
    try:
        requests.post(f"{COOLDOWN_API_URL}/cooldown/{agent_name}", json=payload)
    except requests.exceptions.RequestException as e:
        print(f"[Callback] ERROR: Could not update timestamp, but allowing agent to run. Reason: {e}")

    # --- 4. ALLOW the agent to run ---
    # Returning None tells the ADK to proceed with the agent's execution as normal.
    print(f"[Callback] Check complete for '{agent_name}'. Proceeding with execution.")


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

#REPLACE-worker-agents

#REPLACE-loop-agent

#REPLACE - add A2A