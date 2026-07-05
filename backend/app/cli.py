from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from app.schemas.api import CreateDeckRequest, ValidateRequest
from app.schemas.slide import TableSpec
from app.services.deck_service import DeckService
from app.template_editor.pptx_template import TemplatePptxEditor


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except Exception as exc:
        _print_json({"ok": False, "error": str(exc)}, stderr=True)
        return 1
    _print_json(result)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ppt-agent",
        description="PowerPoint generation and editing CLI for agent workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a PPTX deck from Markdown.")
    create.add_argument("--markdown-file", required=True, help="Path to a Markdown deck spec.")
    create.add_argument("--output", required=True, help="Output PPTX filename under outputs/.")
    create.add_argument("--template-path", help="Optional template PPTX path.")
    create.set_defaults(handler=_handle_create)

    validate = subparsers.add_parser("validate", help="Validate Markdown and/or an existing PPTX.")
    validate.add_argument("--markdown-file", help="Optional Markdown deck spec path.")
    validate.add_argument("--pptx-path", help="Optional PPTX path to validate.")
    validate.set_defaults(handler=_handle_validate)

    inspect = subparsers.add_parser("inspect", help="Inspect editable shapes in a PPTX/template.")
    inspect.add_argument("--pptx-path", help="PPTX path to inspect.")
    inspect.add_argument("--template-path", help="Template path to inspect.")
    inspect.set_defaults(handler=_handle_inspect)

    update = subparsers.add_parser("update", help="Update named text shapes in an existing PPTX.")
    update.add_argument("--pptx-path", required=True, help="Source PPTX path.")
    update.add_argument("--output", required=True, help="Output PPTX filename under outputs/.")
    update.add_argument("--slide-index", type=int, help="Zero-based slide index.")
    update.add_argument("--slide-key", help="Slide key text from the slide_key shape.")
    update.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="SHAPE=TEXT",
        help="Text replacement for a named shape. May be repeated.",
    )
    update.add_argument("--payload-json", help="JSON object with shape names as keys.")
    update.add_argument("--payload-file", help="JSON file with shape names as keys.")
    update.set_defaults(handler=_handle_update)

    set_table = subparsers.add_parser("set-table", help="Replace a named table shape.")
    set_table.add_argument("--pptx-path", required=True, help="Source PPTX path.")
    set_table.add_argument("--output", required=True, help="Output PPTX filename under outputs/.")
    set_table.add_argument("--shape-name", required=True, help="Target table shape name.")
    set_table.add_argument("--slide-index", type=int, help="Zero-based slide index.")
    set_table.add_argument("--slide-key", help="Slide key text from the slide_key shape.")
    set_table.add_argument("--table-json", help="TableSpec JSON object.")
    set_table.add_argument("--table-file", help="TableSpec JSON file.")
    set_table.set_defaults(handler=_handle_set_table)

    return parser


def _handle_create(args: argparse.Namespace) -> dict[str, Any]:
    markdown = _read_text(args.markdown_file)
    response = DeckService().create_deck(
        CreateDeckRequest(
            markdown=markdown,
            template_path=args.template_path,
            output_filename=args.output,
        )
    )
    return response.model_dump()


def _handle_validate(args: argparse.Namespace) -> dict[str, Any]:
    markdown = _read_text(args.markdown_file) if args.markdown_file else None
    response = DeckService().validate(ValidateRequest(markdown=markdown, pptx_path=args.pptx_path))
    return response.model_dump()


def _handle_inspect(args: argparse.Namespace) -> dict[str, Any]:
    path = args.pptx_path or args.template_path
    if not path:
        raise ValueError("--pptx-path or --template-path is required")
    return TemplatePptxEditor().inspect(path)


def _handle_update(args: argparse.Namespace) -> dict[str, Any]:
    payload = _load_mapping(args.payload_json, args.payload_file)
    payload.update(_parse_set_values(args.set))
    if not payload:
        raise ValueError("at least one update value is required via --set, --payload-json, or --payload-file")
    result = TemplatePptxEditor().update_shapes(
        args.pptx_path,
        args.output,
        args.slide_key,
        args.slide_index,
        payload,
    )
    return {
        "pptx_path": str(result.pptx_path),
        "slide_count": result.slide_count,
        "warnings": result.warnings,
    }


def _handle_set_table(args: argparse.Namespace) -> dict[str, Any]:
    payload = _load_mapping(args.table_json, args.table_file)
    if not payload:
        raise ValueError("--table-json or --table-file is required")
    result = TemplatePptxEditor().set_table(
        args.pptx_path,
        args.output,
        args.slide_key,
        args.slide_index,
        args.shape_name,
        TableSpec.model_validate(payload),
    )
    return {
        "pptx_path": str(result.pptx_path),
        "slide_count": result.slide_count,
        "warnings": result.warnings,
    }


def _read_text(path_value: str) -> str:
    return Path(path_value).read_text(encoding="utf-8")


def _load_mapping(json_value: str | None, file_value: str | None) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if file_value:
        loaded = json.loads(Path(file_value).read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError(f"{file_value} must contain a JSON object")
        data.update(loaded)
    if json_value:
        loaded = json.loads(json_value)
        if not isinstance(loaded, dict):
            raise ValueError("JSON value must be an object")
        data.update(loaded)
    return data


def _parse_set_values(values: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"--set value must use SHAPE=TEXT format: {value}")
        key, text = value.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"--set shape name is empty: {value}")
        result[key] = text
    return result


def _print_json(value: dict[str, Any], stderr: bool = False) -> None:
    stream = sys.stderr if stderr else sys.stdout
    print(json.dumps(value, ensure_ascii=False, indent=2), file=stream)


if __name__ == "__main__":
    raise SystemExit(main())
