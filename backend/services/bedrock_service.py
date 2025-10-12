import boto3
import json
import os
from typing import Dict, Any, Optional
import asyncio
from botocore.exceptions import ClientError

class BedrockService:
    def __init__(self):
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.agent_id = os.getenv("BEDROCK_AGENTCORE_AGENT_ID")
        self.model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")

        # Initialize Bedrock clients
        self.bedrock_runtime = boto3.client("bedrock-runtime", region_name=self.region)
        self.bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=self.region)

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

        except Exception as e:
            return {
                "output": {"text": json.dumps({
                    "differential_diagnoses": [
                        {
                            "condition": "Clinical evaluation required",
                            "confidence": 0.3,
                            "reasoning": "Unable to process request with AI model"
                        }
                    ],
                    "recommendations": ["Manual clinical assessment recommended"],
                    "risk_factors": ["Technology limitation"],
                    "next_steps": ["Consult healthcare provider"]
                })}
            }

    def _invoke_model_sync(self, prompt: str) -> Dict[str, Any]:
        """Synchronous model invocation"""

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
        content = response_body['content'][0]['text']

        return {"output": {"text": content}}

    async def analyze_image(self, image_data: bytes, image_type: str) -> Dict[str, Any]:
        """Analyze medical images using multimodal models"""

        # This would use Amazon SageMaker or Bedrock multimodal models
        # For now, return a placeholder response

        return {
            "analysis": "Image analysis not yet implemented",
            "confidence": 0.0,
            "findings": []
        }
