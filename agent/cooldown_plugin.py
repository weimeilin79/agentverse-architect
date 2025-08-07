# cooldown_plugin.py
from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.plugins.base_plugin import BasePlugin
from typing import Optional
from google.genai import types
import requests
from datetime import datetime, timezone, timedelta
import os

COOLDOWN_PERIOD_SECONDS = 60
COOLDOWN_API_URL = os.environ.get("API_SERVER_URL")
print(f"COOLDOWN_API_URL: {COOLDOWN_API_URL}")

class CoolDownPlugin(BasePlugin):
  """A plugin that enforces a cooldown period by checking an external API."""

  def __init__(self, cooldown_seconds: int = COOLDOWN_PERIOD_SECONDS) -> None:
    """Initialize the plugin with counters."""
    super().__init__(name="cool_down_check")
    self.cooldown_period = timedelta(seconds=cooldown_seconds)
    print(f"CooldownPlugin initialized with a {cooldown_seconds}-second cooldown.")
    

  async def before_agent_callback(
      self, *, agent: BaseAgent, callback_context: CallbackContext
  ) -> None:
    """
    This callback checks an external API to see if the agent is on cooldown.
    If it is, it terminates the run by returning a message.
    If it's not, it updates the cooldown timestamp and allows the run to proceed by returning None.
    """
    agent_name = callback_context.agent_name
    print(f"[Callback] Before '{agent_name}': Checking cooldown status...")

    # If the agent is not a main Familiar, skip the entire cooldown process.
    if not agent_name.endswith("_elemental_familiar"):
        print(f"[Callback] Skipping cooldown check for intermediate agent: '{agent_name}'.")
        return None # Allow the agent to proceed immediately.


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
                
        