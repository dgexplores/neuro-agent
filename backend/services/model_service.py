"""Provider selection; the default AWS architecture remains Bedrock."""
import os
from typing import Any, Protocol


class ModelService(Protocol):
    model_id: str

    async def invoke_model_direct(self, prompt: str) -> dict[str, Any]: ...

    async def analyze_image(self, image_data: bytes, image_type: str) -> dict[str, Any]: ...


def create_model_service() -> ModelService:
    provider = os.getenv("MODEL_PROVIDER", "bedrock").strip().lower()
    if provider == "bedrock":
        from .bedrock_service import BedrockService
        return BedrockService()
    if provider == "gemini":
        from .gemini_service import GeminiService
        return GeminiService()
    raise ValueError("MODEL_PROVIDER must be bedrock or gemini")
