# prerequisite/fake_api/main.py (Consolidated Version)
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone
import os
import uvicorn

app = FastAPI()

# --- State Management for Cooldowns ---
# This in-memory dictionary will act as our simple database for cooldowns.
# It will store: { "familiar_name": "ISO_8601_timestamp" }
cooldown_db = {}

class CooldownRequest(BaseModel):
    timestamp: str



@app.get("/")
def read_root():
    return {"message": "The Nexus of Whispers (with Cooldown Logic) is active."}

@app.post("/cryosea_shatter")
def cryosea_shatter():
    """Represents a powerful ice spell from an external source."""
    # This endpoint is kept simple, as requested.
    # The cooldown logic is handled by the plugin calling the /cooldown endpoints.
    return JSONResponse(content={"ability": "cryosea_shatter", "damage_points": 20})

@app.post("/moonlit_cascade")
def moonlit_cascade():
    """Represents a mystical arcane spell from an external source."""
    # This endpoint is also kept simple.
    return JSONResponse(content={"ability": "moonlit_cascade", "damage_points": 25})




@app.get("/cooldown/{familiar_name}")
def get_cooldown_status(familiar_name: str):
    """Returns the last used timestamp for a given Familiar."""
    last_used = cooldown_db.get(familiar_name)
    print(f"[Nexus API] GET Cooldown for '{familiar_name}'. Found: {last_used}")
    if not last_used:
        # If no record exists, the Familiar has never been used.
        return {"time": None}
    return {"time": last_used}

@app.post("/cooldown/{familiar_name}", status_code=status.HTTP_204_NO_CONTENT)
def set_cooldown_timestamp(familiar_name: str, request: CooldownRequest):
    """Updates or sets the cooldown timestamp for a Familiar."""
    print(f"[Nexus API] POST Cooldown for '{familiar_name}' to {request.timestamp}")
    cooldown_db[familiar_name] = request.timestamp
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))