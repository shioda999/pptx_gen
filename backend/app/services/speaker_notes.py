from pathlib import Path

from app.schemas.slide import DeckIR


def write_speaker_notes(deck: DeckIR, output_path: Path) -> None:
    lines: list[str] = ["# Speaker Notes", ""]
    for index, slide in enumerate(deck.slides, start=1):
        lines.extend(
            [
                f"## {index}. {slide.title or slide.slide_id}",
                "",
                f"- slide_id: `{slide.slide_id}`",
                f"- layout: `{slide.layout.value}`",
                "",
                slide.speaker_notes or "",
                "",
            ]
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
