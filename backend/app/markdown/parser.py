from __future__ import annotations

import re
from typing import Any

from app.markdown.simple_yaml import loads_yaml
from app.schemas.slide import DeckIR, slide_from_mapping


FRONTMATTER_RE = re.compile(r"\A\s*---\s*\n(?P<yaml>.*?)\n---\s*(?:\n(?P<body>.*))?\Z", re.DOTALL)
BLOCK_RE = re.compile(r"^:::(?P<name>[A-Za-z0-9_-]+)\s*\n(?P<body>.*?)(?:^:::\s*$)", re.MULTILINE | re.DOTALL)


class MarkdownParseError(ValueError):
    pass


def _strip_code_fences(text: str) -> str:
    return re.sub(r"^```[A-Za-z0-9_-]*\s*$|^````\s*$", "", text, flags=re.MULTILINE).strip()


def _extract_title(body: str) -> str | None:
    match = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def _extract_subtitle(body: str) -> str | None:
    match = re.search(r"^>\s+(.+)$", body, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def _extract_visible_body(body: str) -> str:
    without_blocks = BLOCK_RE.sub("", body)
    lines: list[str] = []
    for raw_line in without_blocks.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            continue
        if stripped.startswith("> "):
            continue
        lines.append(raw_line.rstrip())
    return "\n".join(lines).strip()


def _parse_block(name: str, raw_body: str) -> Any:
    body = _strip_code_fences(raw_body)
    if name == "notes":
        return body
    return loads_yaml(body)


def parse_markdown_slide(markdown: str) -> dict[str, Any]:
    match = FRONTMATTER_RE.match(markdown)
    if not match:
        raise MarkdownParseError("markdown slide must start with YAML frontmatter")
    data = loads_yaml(match.group("yaml"))
    body = match.group("body") or ""
    data.setdefault("title", _extract_title(body) or "")
    subtitle = _extract_subtitle(body)
    if subtitle and not data.get("subtitle"):
        data["subtitle"] = subtitle
    visible_body = _extract_visible_body(body)
    if visible_body:
        if data.get("body"):
            data["body"] = f"{str(data['body']).rstrip()}\n{visible_body}"
        else:
            data["body"] = visible_body

    for block in BLOCK_RE.finditer(body):
        name = block.group("name")
        parsed = _parse_block(name, block.group("body"))
        if name == "diagram":
            data["diagram"] = parsed
        elif name == "table":
            data["table"] = parsed
        elif name == "image":
            data["image"] = parsed
        elif name == "notes":
            data["speaker_notes"] = parsed
    return data


def parse_markdown_deck(markdown: str) -> DeckIR:
    chunks = [markdown.strip()]
    if "<!-- slide -->" in markdown:
        chunks = [chunk.strip() for chunk in re.split(r"^\s*<!--\s*slide\s*-->\s*$", markdown, flags=re.MULTILINE) if chunk.strip()]
    slides = [slide_from_mapping(parse_markdown_slide(chunk)) for chunk in chunks]
    return DeckIR(slides=slides)
