def _coerce_unstructured_payload(raw_text: str) -> Dict[str, Any]:
    compact = raw_text.strip()
    tags = [part.strip(" -•\t") for part in re.split(r",|\\n", compact) if part.strip(" -•\t")]
    return {
        "note": "Model returned plain text instead of JSON",
        "raw": compact,
        "text": compact,
        "summary": compact,
        "tags": tags[:6],
    }


import os
import json
import re
import httpx
from typing import Dict, Any

# ---------------------------------------------------------------------------
# Helper to extract JSON from LLM markdown wrappers
# ---------------------------------------------------------------------------
def _extract_json(text: str) -> str:
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return text.strip()

# ---------------------------------------------------------------------------
# Core inference caller – shared by all AI‑powered endpoints
# ---------------------------------------------------------------------------
async def call_inference(messages: list[Dict[str, str]], max_tokens: int = 512) -> Dict[str, Any]:
    url = "https://inference.do-ai.run/v1/chat/completions"
    model = os.getenv("DO_INFERENCE_MODEL", "openai-gpt-oss-120b")
    api_key = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": max_tokens,
        "temperature": 0.7,
        "stream": False,
    }
    timeout = httpx.Timeout(90.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            # Assuming standard OpenAI style response
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            json_text = _extract_json(content)
            return json.loads(json_text) if json_text else {"note": "AI returned empty response"}
        except Exception as e:
            # Fallback – never raise to route handlers
            return {"note": f"AI service unavailable: {str(e)}"}
