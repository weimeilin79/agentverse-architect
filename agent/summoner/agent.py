from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
import os

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext

FIRE_URL = os.environ.get("FIRE_URL")
WATER_URL = os.environ.get("WATER_URL")
EARTH_URL = os.environ.get("EARTH_URL")

print(f"FIRE_URL: {FIRE_URL}")
print(f"WATER_URL: {WATER_URL}")
print(f"EARTH_URL: {EARTH_URL}")


fire_familiar = RemoteA2aAgent(
    name="fire_familiar",
    description="Fire familiar",
    agent_card=(
        f"{FIRE_URL}/{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

water_familiar = RemoteA2aAgent(
    name="water_familiar",
    description="Water familiar",
    agent_card=(
        f"{WATER_URL}/{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

earth_familiar = RemoteA2aAgent(
    name="earth_familiar",
    description="Earth familiar",
    agent_card=(
        f"{FIRE_URL}/{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)


from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent
import os
from google.adk.tools import load_memory
from google.adk.tools.tool_context import ToolContext

from typing import Dict, Any, Optional

# Assume these environment variables are set
FIRE_URL = os.environ.get("FIRE_URL", "http://fire.example.com")
WATER_URL = os.environ.get("WATER_URL", "http://water.example.com")
EARTH_URL = os.environ.get("EARTH_URL", "http://earth.example.com")

print(f"FIRE_URL: {FIRE_URL}")
print(f"WATER_URL: {WATER_URL}")
print(f"EARTH_URL: {EARTH_URL}")


fire_familiar = RemoteA2aAgent(
    name="fire_familiar",
    description="Fire familiar",
    agent_card=(
        f"{FIRE_URL}/{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

water_familiar = RemoteA2aAgent(
    name="water_familiar",
    description="Water familiar",
    agent_card=(
        f"{WATER_URL}/{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

earth_familiar = RemoteA2aAgent(
    name="earth_familiar",
    description="Earth familiar",
    agent_card=(
        f"{EARTH_URL}/{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

def save_last_summon_after_tool(
    tool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Callback to save the name of the summoned familiar to state after the tool runs.
    """
    familiar_name = tool.name
    print(f"[Callback] After tool '{familiar_name}' executed with args: {args}")

    # Use the tool_context to set the state
    print(f"[Callback] Saving last summoned familiar: {familiar_name}")
    tool_context.state["last_summon"] = familiar_name
    # Important: Return the original, unmodified tool response to the LLM
    return tool_response


root_agent = LlmAgent(
    name="orchestrater_agent",
    model="gemini-2.5-flash",
    instruction="""
        You are the Master Summoner, a grand strategist who orchestrates your Familiars.
        Your mission is to analyze the description of a monster and defeat it by summoning

        You should also know the familiar you called last time or there might be none, 
        And then choose the most effective AND AVAILABLE Familiar from your command list, but do not call that familiar that you called last time!
        
        You MUST follow this thinking process for every command:

        **1. Strategic Analysis:**
        First, analyze the monster's description and the tactical situation.
        Based on your Familiar Doctrines, determine the IDEAL strategy.

        **2. Cooldown Verification:**
        Second, you MUST review the entire conversation history to check the real-time
        cooldown status of all Familiars. A Familiar is ON COOLDOWN and UNAVAILABLE
        if it was summoned less than one minute ago.

        **3. Final Decision & Execution:**
        Based on your analysis and cooldown check, you will now act:
        -   **If your ideal Familiar IS available:** Summon it immediately.
        -   **If your ideal Familiar IS ON COOLDOWN:** You must adapt. Choose another
            Familiar that is AVAILABLE and can still be effective, even if it's not the
            perfect choice. If multiple Familiars are available, you may choose any one of them.
        -   **If ALL Familiars ARE ON COOLDOWN:** You are forbidden from summoning.
            Your ONLY response in this case MUST be: "All Familiars are recovering
            their power. We must wait."
        -   For earth elemental familiar. Always do seismic charge, and start with base damange 1.



        --- FAMILIAR DOCTRINES (Your Toolset) ---
        - `fire_elemental_familiar`: Your specialist for precise, sequential "one-two punch" attacks.
          Ideal monster with Inescapable Reality, Revolutionary Rewrite weakness.
        - `water_elemental_familiar`: Your specialist for overwhelming, simultaneous multi-pronged assaults.
          Ideal for Unbroken Collaboration weakness.
        - `earth_elemental_familiar`: Your specialist for relentless, iterative siege attacks that
          repeatedly charge power. Ideal for Elegant Sufficiency weakness.
    """,
    sub_agents=[fire_familiar, water_familiar, earth_familiar],
    after_tool_callback=save_last_summon_after_tool,
)





from agent_to_a2a import to_a2a

PUBLIC_URL = os.environ.get("PUBLIC_URL","http://0.0.0.0:8080")

if __name__ == "__main__":
    import uvicorn
    a2a_app = to_a2a(root_agent, port=8080, public_url=PUBLIC_URL)
    uvicorn.run(a2a_app, host='0.0.0.0', port=8080)
