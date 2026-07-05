from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.slide import DeckIR, SlideIR


class CreateDeckRequest(BaseModel):
    markdown: str | None = None
    slide: SlideIR | None = None
    deck: DeckIR | None = None
    template_path: str | None = None
    output_filename: str = Field(default="deck.pptx")


class CreateDeckResponse(BaseModel):
    pptx_path: str
    speaker_notes_path: str
    slide_count: int
    warnings: list[str] = Field(default_factory=list)


class ValidateRequest(BaseModel):
    markdown: str | None = None
    slide: SlideIR | None = None
    deck: DeckIR | None = None
    pptx_path: str | None = None


class ValidateResponse(BaseModel):
    ok: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class RenderRequest(BaseModel):
    pptx_path: str
    format: Literal["pdf", "png"] = "pdf"


class GenericTemplateRequest(BaseModel):
    pptx_path: str | None = None
    template_path: str | None = None
    output_filename: str | None = None
    slide_key: str | None = None
    slide_index: int | None = None
    shape_name: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
