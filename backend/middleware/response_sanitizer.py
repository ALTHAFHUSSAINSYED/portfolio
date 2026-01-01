import re
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("ResponseSanitizer")

APOLOGY_PATTERNS = [
    r"\bit seems i may not have\b",
    r"\bi may not have\b",
    r"\bit seems\b",
    r"\bi may\b",
    r"\bi might\b",
    r"\bi apologize\b",
    r"\bsorry\b",
    r"\bapologies\b",
    r"\bfor the confusion\b",
    r"\bi didn.?t explain\b",
    r"\bbased on the provided information\b",
    r"\bas an ai model\b",
    r"\bi don.?t have real-time capabilities\b",
    r"\bi don.?t have access to real-time\b",
    r"\bi can.?t access real-time\b"
]

def strip_apology_boilerplate(text: str) -> str:
    cleaned = text
    for pattern in APOLOGY_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    # Clean up massive whitespace gaps left by removal
    return re.sub(r"\s+", " ", cleaned).strip()


class ResponseSanitizerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Only sanitize chatbot responses
        if (
            request.url.path.endswith("/ask-all-u-bot")
            and isinstance(response, JSONResponse)
        ):
            # Capture the body stream
            body = [section async for section in response.body_iterator]
            response.body_iterator = iter(body)
            body_content = b"".join(body).decode("utf-8")

            try:
                import json
                payload = json.loads(body_content)
                if "reply" in payload and isinstance(payload["reply"], str):
                    original_reply = payload["reply"]
                    sanitized_reply = strip_apology_boilerplate(original_reply)
                    
                    if original_reply != sanitized_reply:
                        logger.info("🧹 Sanitized apology boilerplate from response")
                        payload["reply"] = sanitized_reply
                        
                        return JSONResponse(
                            status_code=response.status_code,
                            content=payload,
                            headers=dict(response.headers),
                        )
            except Exception as e:
                logger.warning(f"Failed to sanitize response: {e}")
                # Fail safe: return original response but we need to reconstruct it
                return JSONResponse(
                    status_code=response.status_code,
                    content=json.loads(body_content),
                    headers=dict(response.headers),
                )

        return response
