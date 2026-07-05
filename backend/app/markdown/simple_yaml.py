from __future__ import annotations

import ast
from typing import Any


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "None", "~"}:
        return None
    if value.startswith("[") or value.startswith("{"):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_simple_yaml(text: str) -> dict[str, Any]:
    lines = [line.rstrip() for line in text.strip().splitlines()]
    root: dict[str, Any] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if ":" not in line:
            index += 1
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if raw == "|":
            block: list[str] = []
            index += 1
            while index < len(lines) and (lines[index].startswith(" ") or not lines[index].strip()):
                block.append(lines[index][2:] if lines[index].startswith("  ") else lines[index].lstrip())
                index += 1
            root[key] = "\n".join(block).strip()
            continue
        if raw:
            root[key] = parse_scalar(raw)
            index += 1
            continue
        index += 1
        if index < len(lines) and lines[index].lstrip().startswith("-"):
            items: list[Any] = []
            while index < len(lines) and lines[index].lstrip().startswith("-"):
                item_text = lines[index].lstrip()[1:].strip()
                if item_text and ":" in item_text and not item_text.startswith(("[", "{")):
                    item_key, item_value = item_text.split(":", 1)
                    item = {item_key.strip(): parse_scalar(item_value.strip())}
                    index += 1
                    while index < len(lines) and lines[index].startswith("    "):
                        child = lines[index].strip()
                        if ":" in child:
                            child_key, child_value = child.split(":", 1)
                            item[child_key.strip()] = parse_scalar(child_value.strip())
                        index += 1
                    items.append(item)
                    continue
                if item_text:
                    items.append(parse_scalar(item_text))
                    index += 1
                    continue
                item: dict[str, Any] = {}
                index += 1
                while index < len(lines) and lines[index].startswith("    "):
                    child = lines[index].strip()
                    if ":" in child:
                        child_key, child_value = child.split(":", 1)
                        item[child_key.strip()] = parse_scalar(child_value.strip())
                    index += 1
                items.append(item)
            root[key] = items
        else:
            nested: dict[str, Any] = {}
            while index < len(lines) and lines[index].startswith("  "):
                child = lines[index].strip()
                if ":" in child:
                    child_key, child_value = child.split(":", 1)
                    nested[child_key.strip()] = parse_scalar(child_value.strip())
                index += 1
            root[key] = nested
    return root


def loads_yaml(text: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text) or {}
        if not isinstance(loaded, dict):
            raise ValueError("YAML content must be an object")
        return loaded
    except ModuleNotFoundError:
        return parse_simple_yaml(text)
