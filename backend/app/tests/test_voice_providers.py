import asyncio
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.voice_provider.retell import RetellProvider
from services.voice_provider.livekit import LiveKitProvider
from schemas.call import UnifiedCall

async def test_normalization():
    print("Testing Retell Normalization...")
    retell = RetellProvider(api_key="test_key")
    retell_payload = {
        "call": {
            "call_id": "123",
            "call_status": "ended",
            "duration_ms": 60000,
            "transcript": "Hello world"
        }
    }
    unified_retell = await retell.normalize_call_data(retell_payload)
    print(f"Retell Unified: {unified_retell.model_dump_json(indent=2)}")
    assert unified_retell.provider_type == "retell"
    assert unified_retell.duration == 60

    print("\nTesting LiveKit Normalization...")
    livekit = LiveKitProvider(api_key="lk_key", api_secret="lk_secret", url="http://localhost:7880")
    livekit_payload = {
        "event": "room_started",
        "room": {
            "sid": "RM_123",
            "name": "test_room"
        }
    }
    unified_livekit = await livekit.normalize_call_data(livekit_payload)
    print(f"LiveKit Unified: {unified_livekit.model_dump_json(indent=2)}")
    assert unified_livekit.provider_type == "livekit"
    assert unified_livekit.provider_call_id == "RM_123"

    print("\nTesting Session Creation (Mocked)...")
    retell_session = await retell.create_session(agent_id="agent_1")
    print(f"Retell Session: {retell_session}")
    
    livekit_session = await livekit.create_session(agent_id="agent_2", metadata={"user_id": "user_456"})
    print(f"LiveKit Session: {livekit_session}")

    print("\nAll tests passed!")

if __name__ == "__main__":
    asyncio.run(test_normalization())
