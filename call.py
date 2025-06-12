from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from livekit.api import LiveKitAPI, CreateRoomRequest
from livekit import api
import time
import json
import os
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")

app = FastAPI()

# LiveKit configuration
api_key = os.getenv("LIVEKIT_API_KEY")
api_secret = os.getenv("LIVEKIT_API_SECRET")
livekit_url = os.getenv("LIVEKIT_URL", "http://localhost:7880")

class CallRequest(BaseModel):
    user_name: str
    phone_number: str

@app.post("/initiate_call")
async def initiate_call(request: CallRequest):
    """
    Initiate an outbound call with user name and phone number
    """
    if not api_key or not api_secret:
        raise HTTPException(
            status_code=500, 
            detail="LiveKit API credentials not configured"
        )
    
    lkapi = LiveKitAPI(url=livekit_url, api_key=api_key, api_secret=api_secret)
    
    try:
        # Read the script from the file
        script_path = "c:\\Users\\Bhakti Gajipara\\Documents\\PragetX\\cold_call_agent\\script.txt"
        with open(script_path, "r") as script_file:
            script_content = script_file.read()

        # Prepare metadata for the agent
        metadata_dict = {
            "phone_number": request.phone_number,
            "transfer_to": None,  # No transfer needed for demo
            "user_name": request.user_name,
            "script": script_content  # Pass the script content
        }
        metadata = json.dumps(metadata_dict)

        # Create a room with unique name
        room_name = f"call-{int(time.time())}-{request.phone_number.replace('+', '').replace(' ', '')}-{uuid.uuid4().hex[:8]}"
        
        room = await lkapi.room.create_room(CreateRoomRequest(
            name=room_name,
            empty_timeout=10 * 60,  # 10 minutes
            max_participants=20,
        ))

        # Create agent dispatch
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name="outbound_cold_caller",  # Must match the agent name in outbound_call_agent.py
                room=room_name, 
                metadata=metadata
            )
        )

        return {
            "message": "Call initiated successfully",
            "call_details": {
                "user_name": request.user_name,
                "phone_number": request.phone_number,
                "room_name": room_name,
                "room_id": room.sid,
                "dispatch_id": dispatch.id,
                "status": "initiated",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate call: {str(e)}"
        )
    
    finally:
        await lkapi.aclose()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)