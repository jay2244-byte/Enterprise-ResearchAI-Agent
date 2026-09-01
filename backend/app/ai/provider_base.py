from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class AIProvider(ABC):
    """Abstract Base Class for all AI model providers."""

    @abstractmethod
    def get_name(self) -> str:
        """Return provider identifier name."""
        pass

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.2) -> str:
        """Generate unstructured text response."""
        pass

    @abstractmethod
    def generate_json(self, prompt: str, schema_description: str = "", system_prompt: str = "") -> Dict[str, Any]:
        """Generate structured JSON response conforming to expected schema."""
        pass

    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Compute embeddings vector for texts."""
        pass
