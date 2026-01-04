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

# Bot name corrections
BOT_NAME_REPLACEMENTS = [
    (r'\bAllu Bot\b', 'Assist Bot'),
    (r'\bAlluBot\b', 'Assist Bot'),
    (r'\bAllu\b(?!\s*Althaf)', 'Assist Bot'),  # Replace "Allu" only if not followed by "Althaf"
]

def strip_apology_boilerplate(text: str) -> str:
    """Remove apology phrases, fix bot names, and clean up formatting artifacts"""
    cleaned = text
    
    # Fix bot name first (critical)
    for pattern, replacement in BOT_NAME_REPLACEMENTS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    # Remove apology patterns
    for pattern in APOLOGY_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    
    # Remove markdown artifacts and formatting issues
    cleaned = re.sub(r'\*\*', '', cleaned)  # Remove bold markdown
    cleaned = re.sub(r'__', '', cleaned)     # Remove underline markdown
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)  # Remove markdown links
    cleaned = re.sub(r'#+\s*', '', cleaned)  # Remove markdown headers
    
    # Fix hyphenated words that should be spaces (e.g., "AI-powered" -> "AI powered" if it's excessive)
    # But keep technical terms like "real-time", "end-to-end"
    technical_terms = ['real-time', 'end-to-end', 'state-of-the-art', 'cloud-native', 'full-stack']
    
    # Clean up excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Remove leading/trailing punctuation artifacts
    cleaned = re.sub(r'^[\s\-:]+|[\s\-:]+$', '', cleaned).strip()
    
    return cleaned


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
