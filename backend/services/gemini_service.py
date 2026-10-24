"""Optional Gemini REST adapter for the Oracle synthetic demonstration."""
import base64
import json
import os
import re
from typing import Any

import httpx
from fastapi import HTTPException


class GeminiService:
    def __init__(self, *, transport: httpx.AsyncBaseTransport | None = None):
        self.model_id = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        if not re.fullmatch(r"gemini-[a-z0-9.-]+", self.model_id):
            raise ValueError("Invalid Gemini model configuration")
        self._transport = transport

    async def _generate(self, parts: list[dict[str, Any]], max_tokens: int) -> str:
        key = os.getenv("GEMINI_API_KEY", "").strip()
        if not key or any(character.isspace() for character in key):
            raise HTTPException(status_code=503, detail="Assessment model unavailable")
        # Keep credentials in a header; URLs and provider errors must not expose them.
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent"
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"maxOutputTokens": max_tokens,
                                 "responseMimeType": "application/json"},
        }
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=3.0, write=5.0, pool=3.0),
                transport=self._transport, follow_redirects=False,
            ) as client:
                response = await client.post(endpoint, json=payload,
                                             headers={"x-goog-api-key": key})
            response.raise_for_status()
            envelope = response.json()
            if not isinstance(envelope, dict):
                raise ValueError("Malformed model response")
            if envelope.get("promptFeedback", {}).get("blockReason"):
                raise ValueError("Blocked prompt")
            candidates = envelope["candidates"]
            if (not isinstance(candidates, list) or len(candidates) != 1
                    or not isinstance(candidates[0], dict)
                    or candidates[0].get("finishReason") != "STOP"):
                raise ValueError("Incomplete or refused response")
            candidate = candidates[0]
            if any(rating.get("blocked") for rating in candidate.get("safetyRatings", [])):
                raise ValueError("Blocked response")
            text = "".join(part["text"] for part in candidate["content"]["parts"]
                           if "text" in part and not part.get("thought"))
            if not text.strip():
                raise ValueError("No model output")
            return text
        except (httpx.HTTPError, ValueError, TypeError, KeyError, IndexError, AttributeError):
            raise HTTPException(status_code=503, detail="Assessment model unavailable") from None

    async def invoke_model_direct(self, prompt: str) -> dict[str, Any]:
        # NeuroAgent validates the assessment JSON and confidence before saving.
        return {"output": {"text": await self._generate([{"text": prompt}], 4096)}}

    async def analyze_image(self, image_data: bytes, image_type: str) -> dict[str, Any]:
        if image_type not in {"image/png", "image/jpeg"}:
            raise HTTPException(status_code=415, detail="Unsupported image type")
        instruction = (
            "For an educational prototype, describe visible image observations only. "
            "Do not claim a diagnosis or clinical validity. Return JSON only with keys "
            "findings (list of strings), limitations (list of strings), impression (string). "
            "State uncertainty and require qualified review."
        )
        parts = [{"inlineData": {"mimeType": image_type,
                                 "data": base64.b64encode(image_data).decode("ascii")}},
                 {"text": instruction}]
        try:
            analysis = json.loads(await self._generate(parts, 2048))
            if (not isinstance(analysis, dict)
                    or not isinstance(analysis.get("impression"), str)
                    or not isinstance(analysis.get("findings"), list)
                    or not all(isinstance(item, str) for item in analysis["findings"])
                    or not isinstance(analysis.get("limitations"), list)
                    or not all(isinstance(item, str) for item in analysis["limitations"])):
                raise ValueError("Malformed image response")
            return analysis
        except (ValueError, TypeError):
            raise HTTPException(status_code=503, detail="Image analysis service unavailable") from None
