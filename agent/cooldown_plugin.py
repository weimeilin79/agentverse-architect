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

#REPLACE-plugin