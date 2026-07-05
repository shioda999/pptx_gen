from pathlib import Path

from app.schemas.api import CreateDeckRequest, ValidateRequest
from app.services.deck_service import DeckService


def test_generated_pptx_layout_validation():
    project_root = Path(__file__).resolve().parents[2]
    markdown = (project_root / "examples" / "architecture-flow.md").read_text(encoding="utf-8")
    service = DeckService()
    created = service.create_deck(CreateDeckRequest(markdown=markdown, output_filename="pytest-architecture.pptx"))
    result = service.validate(ValidateRequest(pptx_path=created.pptx_path))
    assert result.ok
