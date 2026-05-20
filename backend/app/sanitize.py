"""Input sanitization helpers used in all request schemas and document routes."""

import json

import bleach

_ALLOWED_NODE_TYPES = {"doc", "paragraph", "heading", "requirement-ref", "text"}
_MAX_DOCUMENT_CHARS = 1_000_000


def sanitize_text(value: str, max_len: int) -> str:
    """Enforce UTF-8, strip all HTML tags, and check max length.

    Raises ValueError if the cleaned text exceeds max_len characters.
    """
    value = value.encode("utf-8", errors="replace").decode("utf-8")
    value = bleach.clean(value, tags=[], strip=True)
    if len(value) > max_len:
        raise ValueError(f"Value exceeds maximum length of {max_len} characters.")
    return value


def sanitize_document_content(content: dict) -> dict:
    """Validate and sanitize a TipTap document_content dict.

    Recursively checks that all node types are in the allowlist, sanitizes
    text node values via bleach, enforces heading level 1–8, and validates
    requirement-ref attrs. Raises ValueError on any violation.
    Raises ValueError if serialized JSON exceeds 1,000,000 chars.
    """
    serialized = json.dumps(content)
    if len(serialized) > _MAX_DOCUMENT_CHARS:
        raise ValueError("document_content exceeds maximum size of 1,000,000 characters.")
    _walk_node(content)
    return content


def _walk_node(node: dict) -> None:
    """Recursively validate and sanitize a single document node in-place."""
    if not isinstance(node, dict):
        raise ValueError("Each document node must be a JSON object.")
    node_type = node.get("type")
    if node_type not in _ALLOWED_NODE_TYPES:
        raise ValueError(
            f"Node type '{node_type}' is not allowed. "
            f"Allowed types: {sorted(_ALLOWED_NODE_TYPES)}"
        )
    if node_type == "text":
        raw = node.get("text", "")
        if not isinstance(raw, str):
            raise ValueError("text node 'text' field must be a string.")
        node["text"] = bleach.clean(raw, tags=[], strip=True)
    elif node_type == "heading":
        attrs = node.get("attrs", {})
        level = attrs.get("level")
        if level not in range(1, 9):
            raise ValueError(f"Heading level must be 1–8, got {level!r}.")
    elif node_type == "requirement-ref":
        attrs = node.get("attrs", {})
        req_id = attrs.get("requirement_id")
        proj_id = attrs.get("project_id")
        if not isinstance(req_id, int):
            raise ValueError("requirement-ref node must have integer 'requirement_id' attr.")
        if not isinstance(proj_id, str) or len(proj_id) > 100:
            raise ValueError(
                "requirement-ref node must have string 'project_id' attr (max 100 chars)."
            )
        attrs["project_id"] = sanitize_text(proj_id, 100)
    for child in node.get("content", []):
        _walk_node(child)
