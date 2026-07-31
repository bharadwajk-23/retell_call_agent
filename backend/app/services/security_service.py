"""HMAC signature verification for inbound Retell webhooks."""

from retell.lib.webhook_auth import verify as _verify_signature


def verify_retell_signature(body: bytes, secret: str, signature: str) -> bool:
    """Verify the `x-retell-signature` header against the raw request body."""
    if not signature or not secret:
        return False
    return bool(_verify_signature(body.decode("utf-8"), secret, signature))
