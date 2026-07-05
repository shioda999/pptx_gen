from pathlib import Path

from app.schemas.api import CreateDeckRequest
from app.services.deck_service import DeckService


def test_create_deck_from_markdown(tmp_path, monkeypatch):
    from app.core.config import Settings

    project_root = Path(__file__).resolve().parents[2]
    settings = Settings(project_root=project_root)
    monkeypatch.setattr("app.core.config.get_settings", lambda: settings)
    markdown = (project_root / "examples" / "table.md").read_text(encoding="utf-8")
    response = DeckService(settings).create_deck(CreateDeckRequest(markdown=markdown, output_filename="pytest-table.pptx"))
    assert Path(response.pptx_path).exists()
    assert Path(response.speaker_notes_path).exists()
    assert response.slide_count == 1
