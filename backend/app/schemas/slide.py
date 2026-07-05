from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SlideMode(str, Enum):
    generated = "generated"
    template = "template"


class LayoutName(str, Enum):
    title = "title"
    section = "section"
    text_image = "text-image"
    architecture_flow = "architecture-flow"
    comparison = "comparison"
    metric_cards = "metric-cards"
    table = "table"
    timeline = "timeline"
    process_flow = "process-flow"
    summary = "summary"


class ThemeName(str, Enum):
    modern_tech = "modern-tech"
    neutral = "neutral"


class TemplateSlideType(str, Enum):
    title = "title"
    agenda = "agenda"
    section = "section"
    content = "content"


class TemplateSlideVariant(str, Enum):
    generic = "generic"
    cover = "cover"
    text = "text"
    table = "table"
    diagram = "diagram"
    two_column = "two_column"
    image = "image"
    summary = "summary"
    profile = "profile"


class ImageFit(str, Enum):
    contain = "contain"
    cover = "cover"
    crop = "crop"


class DiagramNode(BaseModel):
    id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_.-]+$")
    label: str = Field(min_length=1)
    kind: str = Field(default="service", min_length=1)
    group: str | None = None


class DiagramEdge(BaseModel):
    source: str = Field(alias="from")
    target: str = Field(alias="to")

    model_config = ConfigDict(populate_by_name=True)


class DiagramSpec(BaseModel):
    nodes: list[DiagramNode] = Field(min_length=1)
    edges: list[DiagramEdge] = Field(default_factory=list)
    direction: Literal["horizontal", "vertical"] = "horizontal"

    @model_validator(mode="after")
    def validate_edges(self) -> "DiagramSpec":
        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                raise ValueError(f"diagram edge references missing node: {edge.source}->{edge.target}")
        return self


class TableSpec(BaseModel):
    headers: list[str] = Field(min_length=1)
    rows: list[list[str]] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_column_counts(self) -> "TableSpec":
        width = len(self.headers)
        for index, row in enumerate(self.rows):
            if len(row) != width:
                raise ValueError(f"table row {index} has {len(row)} cells; expected {width}")
        return self


class ImageSpec(BaseModel):
    path: str
    fit: ImageFit = ImageFit.contain
    target: str = "hero_image"

    @field_validator("path")
    @classmethod
    def reject_urls(cls, value: str) -> str:
        lowered = value.lower()
        if lowered.startswith(("http://", "https://", "file://")):
            raise ValueError("image path must be a local path, not a URL")
        return value


class SlideIR(BaseModel):
    slide_id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_.-]+$")
    mode: SlideMode = SlideMode.generated
    layout: LayoutName
    theme: ThemeName = ThemeName.modern_tech
    title: str = Field(default="", max_length=240)
    subtitle: str | None = Field(default=None, max_length=400)
    body: str | None = None
    diagram: DiagramSpec | None = None
    table: TableSpec | None = None
    image: ImageSpec | None = None
    speaker_notes: str | None = None
    slide_key: str | None = None
    slide_type: TemplateSlideType = TemplateSlideType.content
    slide_variant: TemplateSlideVariant = TemplateSlideVariant.generic

    @model_validator(mode="after")
    def validate_layout_payload(self) -> "SlideIR":
        if self.mode != SlideMode.generated:
            return self
        required = {
            LayoutName.architecture_flow: self.diagram,
            LayoutName.table: self.table,
        }
        missing = [layout.value for layout, value in required.items() if self.layout == layout and value is None]
        if missing:
            raise ValueError(f"layout requires missing payload: {', '.join(missing)}")
        return self


class DeckIR(BaseModel):
    slides: list[SlideIR] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_slide_ids(self) -> "DeckIR":
        seen: set[str] = set()
        for slide in self.slides:
            if slide.slide_id in seen:
                raise ValueError(f"duplicate slide_id: {slide.slide_id}")
            seen.add(slide.slide_id)
        return self


def slide_from_mapping(data: dict) -> SlideIR:
    if "slide_type" not in data and "category" in data:
        data["slide_type"] = data["category"]
    if "slide_variant" not in data and "variant" in data:
        data["slide_variant"] = data["variant"]
    if "slide_variant" not in data:
        layout = data.get("layout")
        if "table" in data or layout == LayoutName.table.value:
            data["slide_variant"] = TemplateSlideVariant.table.value
        elif "diagram" in data or layout in {LayoutName.architecture_flow.value, LayoutName.process_flow.value}:
            data["slide_variant"] = TemplateSlideVariant.diagram.value
        elif layout == LayoutName.summary.value:
            data["slide_variant"] = TemplateSlideVariant.summary.value
        elif layout == LayoutName.title.value:
            data["slide_variant"] = TemplateSlideVariant.cover.value
        else:
            data["slide_variant"] = TemplateSlideVariant.text.value
    if "diagram" in data and isinstance(data["diagram"], dict):
        for edge in data["diagram"].get("edges", []):
            if "source" not in edge and "from" in edge:
                edge["source"] = edge["from"]
            if "target" not in edge and "to" in edge:
                edge["target"] = edge["to"]
        for node in data["diagram"].get("nodes", []):
            if "kind" not in node and "type" in node:
                node["kind"] = node["type"]
    return SlideIR.model_validate(data)


def validate_image_file(image: ImageSpec, base_dir: Path, max_bytes: int) -> Path:
    path = Path(image.path)
    resolved = (base_dir / path).resolve() if not path.is_absolute() else path.resolve()
    if base_dir.resolve() not in resolved.parents and resolved != base_dir.resolve():
        raise ValueError(f"image path escapes project root: {image.path}")
    if not resolved.exists():
        raise ValueError(f"image does not exist: {image.path}")
    if resolved.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        raise ValueError("image must be png, jpg, or jpeg")
    if resolved.stat().st_size > max_bytes:
        raise ValueError("image exceeds maximum size")
    return resolved
