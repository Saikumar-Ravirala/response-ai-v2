from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from schemas.call import UnifiedCall

class VoiceProviderService(ABC):
    """
    Abstract base class for all voice providers.
    Ensures a consistent interface for the business logic.
    """

    @abstractmethod
    async def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all agents available for the provider.
        """
        pass

    @abstractmethod
    async def get_agent_details(self, agent_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information for a specific agent.
        """
        pass

    @abstractmethod
    async def create_session(self, agent_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new session (web call for Retell, room/token for LiveKit).
        """
        pass

    @abstractmethod
    async def normalize_call_data(self, raw_payload: Dict[str, Any]) -> UnifiedCall:
        """
        Convert a provider-specific payload into a UnifiedCall object.
        """
        pass

    @abstractmethod
    async def validate_webhook(self, headers: Dict[str, str], body: bytes, secret: str) -> bool:
        """
        Validate that a webhook request actually came from the provider.
        """
        pass
