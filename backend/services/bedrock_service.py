import base64
import boto3
from fastapi import HTTPException
import json
import os
from typing import Dict, Any, Optional
import asyncio
from botocore.exceptions import ClientError

class BedrockService:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.agent_id = os.getenv("BEDROCK_AGENTCORE_AGENT_ID")
        # Use Mistral Large if Claude models are not available
        self.model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")

        # Initialize Bedrock clients
        self._bedrock_runtime = None
        self._bedrock_agent_runtime = None

    @property
    def bedrock_runtime(self):
        if self._bedrock_runtime is None:
            self._bedrock_runtime = boto3.client("bedrock-runtime", region_name=self.region)
        return self._bedrock_runtime

    @bedrock_runtime.setter
    def bedrock_runtime(self, client):
        self._bedrock_runtime = client

    @property
    def bedrock_agent_runtime(self):
        if self._bedrock_agent_runtime is None:
            self._bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=self.region)
        return self._bedrock_agent_runtime

    async def invoke_agent(self, agent_id: str, session_id: str, input_text: str) -> Dict[str, Any]:
        """Invoke Bedrock AgentCore agent"""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._invoke_agent_sync,
                agent_id,
                session_id,
                input_text
            )
            return response

        except ClientError as e:
            print(f"Bedrock Agent error: {e}")
            # Fallback to direct model invocation
            return await self.invoke_model_direct(input_text)

    def _invoke_agent_sync(self, agent_id: str, session_id: str, input_text: str) -> Dict[str, Any]:
        """Synchronous agent invocation"""

        try:
            response = self.bedrock_agent_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId="TSTALIASID",  # Test alias
                sessionId=session_id,
                inputText=input_text
            )

            # Process streaming response
            event_stream = response['completion']
            full_response = ""

            for event in event_stream:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        full_response += chunk['bytes'].decode('utf-8')

            return {
                "output": {"text": full_response},
                "session_id": session_id
            }

        except Exception as e:
            raise ClientError(
                error_response={'Error': {'Code': 'AgentInvocationError', 'Message': str(e)}},
                operation_name='invoke_agent'
            )

    async def invoke_model_direct(self, prompt: str) -> Dict[str, Any]:
        """Direct model invocation as fallback"""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._invoke_model_sync,
                prompt
            )
            return response

        except Exception:
            raise HTTPException(status_code=503, detail="Assessment model unavailable")

    def _invoke_model_sync(self, prompt: str) -> Dict[str, Any]:
        """Synchronous model invocation - supports both Anthropic and Mistral models"""

        # Detect model type and use appropriate format
        if "mistral" in self.model_id.lower():
            # Mistral model format
            body = json.dumps({
                "prompt": f"<s>[INST] {prompt} [/INST]",
                "max_tokens": 2048,
                "temperature": 0.1
            })
        else:
            # Anthropic Claude model format
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 4096,
                "temperature": 0.1
            })

        response = self.bedrock_runtime.invoke_model(
            body=body,
            modelId=self.model_id,
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(response['body'].read())

        # Extract content based on model type
        if "mistral" in self.model_id.lower():
            # Mistral response format
            content = response_body['outputs'][0]['text']
        else:
            # Anthropic Claude response format
            content = response_body['content'][0]['text']

        return {"output": {"text": content}}

    async def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Call a configured Claude multimodal model; never synthesize findings."""
        if "anthropic.claude-3" not in self.model_id:
            raise HTTPException(status_code=501, detail="Configured model does not support this image adapter")
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "temperature": 0.0,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": image_type,
                 "data": base64.b64encode(image_data).decode("ascii")}},
                {"type": "text", "text": "For an educational prototype, describe visible image observations only. Do not claim a diagnosis or clinical validity. Return JSON only with keys findings (list of strings), limitations (list of strings), impression (string). State uncertainty and require qualified review."}
            ]}]
        }
        try:
            response = await asyncio.to_thread(
                self.bedrock_runtime.invoke_model, modelId=self.model_id,
                body=json.dumps(body), accept="application/json", contentType="application/json"
            )
            envelope = json.loads(response["body"].read())
            text = "".join(part.get("text", "") for part in envelope["content"])
            analysis = json.loads(text)
            if (not isinstance(analysis, dict)
                or not isinstance(analysis.get("impression"), str)
                or not isinstance(analysis.get("findings"), list)
                or not all(isinstance(x, str) for x in analysis["findings"])
                or not isinstance(analysis.get("limitations"), list)
                or not all(isinstance(x, str) for x in analysis["limitations"])):
                raise ValueError("Invalid image response")
            return analysis
        except Exception:
            raise HTTPException(status_code=503, detail="Image analysis service unavailable")
