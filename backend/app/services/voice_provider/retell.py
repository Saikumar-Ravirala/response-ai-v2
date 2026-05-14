import hmac
import hashlib
import json
import httpx
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
        """
        Lists all Retell agents.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/list-agents",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error listing agents: {e}")
                return []

    async def get_agent_details(self, agent_id: str) -> Dict[str, Any]:
        """
        Gets details for a specific Retell agent.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/get-agent/{agent_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error getting agent details: {e}")
                return {}

    async def create_session(self, agent_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Creates a Retell web call session using the v2 endpoint.
        """
        async with httpx.AsyncClient() as client:
            try:
                payload = {"agent_id": agent_id}
                if metadata:
                    payload["metadata"] = metadata
                
                response = await client.post(
                    f"{self.base_url}/v2/create-web-call",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error creating web call: {e}")
                return {}

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
