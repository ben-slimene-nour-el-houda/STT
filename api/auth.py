from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from common.settings import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key from request headers.
    Raises 401 if the key is missing or not in the allowed list.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
    if api_key not in settings.API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
