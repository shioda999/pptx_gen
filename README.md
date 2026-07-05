# PPT Agent Core

FastAPI based PowerPoint generation core for Dify, Hermes Agent, and a future MCP wrapper.

Phase 1 implements:

- Markdown slide specs with YAML frontmatter and `:::diagram`, `:::table`, `:::image`, `:::notes` blocks
- Slide IR validation with Pydantic
- Generated PPTX mode using `python-pptx`
- Layouts: `architecture-flow`, `text-image`, `table`
- `speaker_notes.md` output
- Rule-based PPTX layout validation
- Minimal template mode using `python-pptx`: copy a `.pptx`, inspect `slide_key`, and update named shapes

Rendering, slide insertion, and PowerPoint notes-pane writing still return `501` until the Phase 2/3 renderer and Windows PowerPoint COM editor are added.

## Setup

```powershell
cd ppt-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

In this Codex workspace, the bundled Python already includes `pydantic` and `python-pptx`; install `fastapi`, `uvicorn`, `PyYAML`, and `pytest` in your runtime environment before serving the API.

## Run

```powershell
cd ppt-agent\backend
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Agent-Friendly CLI

The CLI runs the same core services without starting FastAPI. Run it from
`ppt-agent/backend` so Python can import `app`.

Create a deck:

```powershell
python -m app.cli create `
  --markdown-file ..\examples\gpu-cluster-architecture.md `
  --output gpu-cluster.pptx
```

Create from a local template:

```powershell
python -m app.cli create `
  --markdown-file ..\examples\codex-self-intro.md `
  --template-path templates\local-template.pptx `
  --output template-based.pptx
```

Validate Markdown and/or PPTX:

```powershell
python -m app.cli validate --markdown-file ..\examples\table.md
python -m app.cli validate --pptx-path outputs\gpu-cluster.pptx
```

Inspect editable shapes:

```powershell
python -m app.cli inspect --pptx-path outputs\gpu-cluster.pptx
```

Update named shapes in an existing deck:

```powershell
python -m app.cli update `
  --pptx-path outputs\gpu-cluster.pptx `
  --output gpu-cluster-edited.pptx `
  --slide-index 0 `
  --set "title=GPUクラスタ構成と運用設計" `
  --set "body=クラスタの見方`n  - GPU node / network / storageを一体で見る"
```

For larger updates, pass a JSON object:

```powershell
python -m app.cli update `
  --pptx-path outputs\gpu-cluster.pptx `
  --output gpu-cluster-edited.pptx `
  --slide-key gpu-cluster-overview-1 `
  --payload-file update-payload.json
```

All CLI commands print JSON to stdout and errors as JSON to stderr. This keeps
the interface easy for agents and future MCP wrappers to consume.

## Create A Deck

```bash
curl -X POST http://127.0.0.1:8000/create-deck \
  -H "Content-Type: application/json" \
  -d '{"markdown":"---\nslide_id: benchmark-results\nmode: generated\nlayout: table\ntheme: modern-tech\ntitle: 推論性能比較\n---\n\n:::table\nheaders:\n  - 同時実行数\n  - 生成速度\nrows:\n  - [\"1\", \"10 tok/s\"]\n:::\n","output_filename":"benchmark.pptx"}'
```

Outputs are written under `outputs/`.

## Create From A Template

Template mode copies the source `.pptx` and updates only named shapes. The source template is not modified.
When `template_path` has a sibling `*.metadata.json`, the renderer selects only the slides needed by the Markdown input.

```bash
curl -X POST http://127.0.0.1:8000/create-deck \
  -H "Content-Type: application/json" \
  -d '{"template_path":"templates/codex-template.pptx","markdown":"...","output_filename":"template-based.pptx"}'
```

Inspect a template:

```bash
curl -X POST http://127.0.0.1:8000/inspect-presentation \
  -H "Content-Type: application/json" \
  -d '{"template_path":"templates/codex-template.pptx"}'
```

Supported named shape updates:

- `slide_key` identifies the slide
- `title`, `subtitle`, `body` are text replacements
- `diagram_area` is replaced with an auto-laid-out architecture flow
- `table_area` is replaced with a generated table
- image targets such as `hero_image` can be replaced by `/set-image`

Table behavior:

- If a template slide already contains a table placeholder, the existing table is reused and the editor first tries to infer table colors from its cells.
- Extra rows and columns are removed when the input table is smaller than the placeholder.
- If colors cannot be read from the template, the default table style is used: dark blue header, white header text, and alternating light gray / white body rows.
- If no table exists, a default styled table is generated with the same default colors.

### Template Metadata

Place metadata next to the template:

```text
templates/imported/template3.pptx
templates/imported/template3.metadata.json
```

Metadata classifies each template slide:

```json
{
  "template": "template3.pptx",
  "version": 1,
  "categories": ["title", "agenda", "section", "content"],
  "slides": [
    {"index": 0, "category": "title", "layout": "タイトルのみ"},
    {"index": 1, "category": "agenda", "layout": "コンテンツ 2"},
    {"index": 3, "category": "section", "layout": "タイトル + サブタイトル + 画像"},
    {"index": 4, "category": "content", "layout": "コンテンツ 1"}
  ]
}
```

Markdown can request a category per slide:

```md
---
slide_id: cover
layout: title
slide_type: title
slide_variant: cover
title: Project Overview
---
```

Allowed `slide_type` values are `title`, `agenda`, `section`, and `content`. If omitted, `content` is used.

Use `slide_variant` to pick a better slide within that category:

- `cover`
- `text`
- `table`
- `diagram`
- `two_column`
- `image`
- `summary`
- `profile`
- `generic`

If `slide_variant` is omitted, it is inferred from the slide content and layout. For example, `layout: table` or a `:::table` block becomes `table`; `architecture-flow` or `:::diagram` becomes `diagram`.

Selection priority:

1. Matching `slide_type + slide_variant`
2. Matching `slide_type + generic`
3. Matching `slide_type`
4. Matching `content + slide_variant`
5. Any unused template slide

The output deck is ordered by the Markdown slides, not by the original template order.

## Markdown Spec

Each slide starts with YAML frontmatter:

```md
---
slide_id: vllm-architecture
mode: generated
layout: architecture-flow
theme: modern-tech
title: vLLM推論基盤の構成
subtitle: API Gateway経由で複数のvLLM Podへリクエストを分散
---
```

Supported custom blocks:

- `:::diagram` for `architecture-flow`
- `:::table` for table data
- `:::image` for local images only
- `:::notes` for speaker notes

Use `<!-- slide -->` between slide specs to create a multi-slide deck.

## Linux Generated Mode

Generated mode uses `python-pptx` and does not require PowerPoint. PDF/PNG rendering is reserved for Phase 2, where LibreOffice headless can be used as a fallback renderer.

## Windows Template Mode

The current minimal template mode uses `python-pptx`; the source deck is copied to `outputs/` before editing. Full-fidelity Windows template mode should use Microsoft PowerPoint COM Automation via `pywin32` in Phase 3.

In PowerPoint, open the Selection Pane and name editable shapes with stable names such as:

- `title`
- `subtitle`
- `body`
- `hero_image`
- `diagram_area`
- `table_area`
- `footer`
- `slide_key`

Agents should address slides by `slide_key`, not only by page index.

## Dify / Hermes / MCP Shape

The current API is intentionally tool-like:

- `/create-deck` maps to a future `create_deck` MCP tool
- `/validate` maps to a future `validate_deck` MCP tool
- template endpoints are reserved so the MCP wrapper can keep stable tool names

The agent should send Markdown or Slide IR JSON only. It must not send Python, PowerShell, or arbitrary executable instructions.
