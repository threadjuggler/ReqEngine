"""Input sanitization helper used in all request schemas."""

import bleach


def sanitize_text(value: str, max_len: int) -> str:
    """Enforce UTF-8, strip all HTML tags, and check max length.

    Raises ValueError if the cleaned text exceeds max_len characters.
    """
    # bleach operates on str; encode/decode round-trip validates UTF-8
    value = value.encode("utf-8", errors="replace").decode("utf-8")
    value = bleach.clean(value, tags=[], strip=True)
    if len(value) > max_len:
        raise ValueError(f"Value exceeds maximum length of {max_len} characters.")
    return value
