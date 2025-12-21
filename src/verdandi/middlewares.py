import hmac

from fastapi import (
    status,
    HTTPException,
)

from verdandi.state import DepState


async def auth_middleware(state: DepState, secret: str | None = None):
    expected_secret = state.configuration.secret()

    if expected_secret is None:
        return

    if secret is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No secret is provided",
        )

    if not hmac.compare_digest(expected_secret, secret):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provided secret does not match",
        )
