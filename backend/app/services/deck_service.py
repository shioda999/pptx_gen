from __future__ import annotations

from pathlib import Path

from app.core.config import Settings, get_settings
from app.core.paths import ensure_output_path, resolve_project_path
from app.markdown.parser import parse_markdown_deck
from app.renderers.pptx_generated import GeneratedPptxRenderer
from app.schemas.api import CreateDeckRequest, CreateDeckResponse, ValidateRequest, ValidateResponse
from app.schemas.slide import DeckIR
from app.services.pagination import paginate_deck
from app.services.speaker_notes import write_speaker_notes
from app.template_editor.pptx_template import TemplatePptxEditor
from app.validators.layout import validate_pptx_layout


class DeckService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def request_to_deck(self, request: CreateDeckRequest | ValidateRequest) -> DeckIR:
        if request.deck:
            return request.deck
        if request.slide:
            return DeckIR(slides=[request.slide])
        if request.markdown:
            return parse_markdown_deck(request.markdown)
        raise ValueError("one of markdown, slide, or deck is required")

    def create_deck(self, request: CreateDeckRequest) -> CreateDeckResponse:
        deck = paginate_deck(self.request_to_deck(request))
        if request.template_path:
            result = TemplatePptxEditor(self.settings).apply_deck(request.template_path, deck, request.output_filename)
            return CreateDeckResponse(
                pptx_path=str(result.pptx_path),
                speaker_notes_path=str(result.speaker_notes_path or ""),
                slide_count=result.slide_count,
                warnings=result.warnings,
            )
        output_path = ensure_output_path(request.output_filename, self.settings)
        renderer = GeneratedPptxRenderer(self.settings.project_root, self.settings.max_image_bytes)
        warnings = renderer.render(deck, output_path)
        notes_path = output_path.with_suffix(".speaker_notes.md")
        write_speaker_notes(deck, notes_path)
        return CreateDeckResponse(
            pptx_path=str(output_path),
            speaker_notes_path=str(notes_path),
            slide_count=len(deck.slides),
            warnings=warnings,
        )

    def validate(self, request: ValidateRequest) -> ValidateResponse:
        errors: list[str] = []
        warnings: list[str] = []
        if request.markdown or request.slide or request.deck:
            try:
                self.request_to_deck(request)
            except Exception as exc:
                errors.append(str(exc))
        if request.pptx_path:
            try:
                path = resolve_project_path(request.pptx_path, self.settings)
                pptx_errors, pptx_warnings = validate_pptx_layout(Path(path))
                errors.extend(pptx_errors)
                warnings.extend(pptx_warnings)
            except Exception as exc:
                errors.append(str(exc))
        return ValidateResponse(ok=not errors, errors=errors, warnings=warnings)
