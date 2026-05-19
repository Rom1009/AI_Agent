class TransientAIError(Exception):
    """Temporary error. Retry is allowed"""

class PermanentAIError(Exception):
    """Permanent error. Retry is not allowed"""