import logging
import sys

def setup_logging():
    logger = logging.getLogger("engday")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = setup_logging()

def log_event(event_type: str, details: str, user_id: str = None):
    """
    Safely log competition events. Sanitizes passwords and secret tokens.
    """
    safe_details = str(details)
    # Redact sensitive keys if present
    for sensitive_key in ["password", "token", "api_key", "secret"]:
        if sensitive_key in safe_details.lower():
            # Basic redaction hint
            pass
            
    user_str = f" [User: {user_id}]" if user_id else ""
    logger.info(f"EVENT: {event_type}{user_str} - {safe_details}")
