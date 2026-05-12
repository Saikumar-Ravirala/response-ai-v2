import hmac
import hashlib
import json
from typing import List, Dict, Any, Optional
from services.voice_provider.base import VoiceProviderService
from schemas.call import UnifiedCall

class RetellProvider(VoiceProviderService):
    """
    Retell AI provider implementation.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.retellai.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def list_agents(self) -> List[Dict[str, Any]]:
        # Placeholder for actual API call
        # In a real scenario, we would use httpx.AsyncClient
        return []

    async def get_agent_details(self, agent_id: str) -> Dict[str, Any]:
        # Placeholder for actual API call
        return {"agent_id": agent_id}

    async def create_session(self, agent_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Creates a Retell web call session.
        """
        # Logic to call /create-web-call
        return {
            "access_token": "mock_retell_token",
            "call_id": "mock_call_id"
        }

    async def normalize_call_data(self, raw_payload: Dict[str, Any]) -> UnifiedCall:
        """
        Maps Retell specific webhook payload to UnifiedCall.
        """
        call_data = raw_payload.get("call", {})
        return UnifiedCall(
            provider_type="retell",
            provider_call_id=call_data.get("call_id"),
            status=call_data.get("call_status"),
            duration=call_data.get("duration_ms", 0) // 1000 if call_data.get("duration_ms") else 0,
            transcript=call_data.get("transcript"),
            raw_data=raw_payload
        )

    async def validate_webhook(self, headers: Dict[str, str], body: bytes, secret: str) -> bool:
        """
        Validates Retell HMAC signature.
        """
        signature = headers.get("x-retell-signature")
        if not signature:
            return False
        
        expected_signature = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
