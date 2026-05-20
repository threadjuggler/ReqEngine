"""FastAPI dependencies shared across routers."""


def get_current_user() -> str:
    """Return the hardcoded current user name for step 1 (auth comes later)."""
    return "User1"
