from app.schemas.slide import DeckIR, LayoutName, SlideIR
from app.services.pagination import _chunk_body, paginate_deck


def test_paginate_long_hierarchy_body():
    lines: list[str] = []
    for index in range(1, 9):
        lines.extend(
            [
                f"Section {index}",
                "  - first detail",
                "    - nested detail",
                "    - another nested detail",
            ]
        )
    body = "\n".join(lines)
    deck = DeckIR(
        slides=[
            SlideIR(
                slide_id="long-body",
                layout=LayoutName.summary,
                title="Long Body",
                body=body,
            )
        ]
    )

    paginated = paginate_deck(deck)

    assert len(paginated.slides) > 1
    assert len({slide.slide_id for slide in paginated.slides}) == len(paginated.slides)
    assert paginated.slides[0].title == "Long Body"
    assert paginated.slides[1].title == "Long Body（続き）"


def test_chunk_body_balances_small_remainder():
    body = "\n".join(
        [
            "First group",
            "  - detail",
            "  - detail",
            "Second group",
            "  - detail",
            "  - detail",
            "Third group",
            "  - detail",
        ]
    )

    chunks = _chunk_body(body, capacity=7.0)

    assert len(chunks) == 2
    assert "First group" in chunks[0]
    assert "Second group" not in chunks[0]
    assert "Second group" in chunks[1]
    assert "Third group" in chunks[1]
