from pathlib import Path

from app.markdown.parser import parse_markdown_deck


def test_parse_architecture_flow_sample():
    project_root = Path(__file__).resolve().parents[2]
    markdown = (project_root / "examples" / "architecture-flow.md").read_text(encoding="utf-8")
    deck = parse_markdown_deck(markdown)
    slide = deck.slides[0]
    assert slide.slide_id == "vllm-architecture"
    assert slide.diagram is not None
    assert len(slide.diagram.nodes) == 4
    assert slide.speaker_notes


def test_parse_visible_markdown_body_after_frontmatter():
    markdown = """---
slide_id: visible-body
layout: summary
title: Visible Body
---

# Visible Body
> Subtitle line

Main message
  - nested detail
Final message should remain
"""

    deck = parse_markdown_deck(markdown)
    slide = deck.slides[0]

    assert slide.subtitle == "Subtitle line"
    assert slide.body is not None
    assert "Main message" in slide.body
    assert "nested detail" in slide.body
    assert slide.body.endswith("Final message should remain")


def test_parse_visible_markdown_appends_to_yaml_body():
    markdown = """---
slide_id: visible-body-append
layout: summary
title: Visible Body Append
body: |
  YAML message
---

Trailing message
"""

    deck = parse_markdown_deck(markdown)
    slide = deck.slides[0]

    assert slide.body == "YAML message\nTrailing message"
