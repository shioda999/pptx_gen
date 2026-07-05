from __future__ import annotations

from math import ceil

from app.schemas.slide import DeckIR, LayoutName, SlideIR, TemplateSlideVariant


BODY_CAPACITY_BY_LAYOUT = {
    LayoutName.architecture_flow: 10.5,
    LayoutName.text_image: 14.5,
    LayoutName.table: 0.0,
    LayoutName.summary: 16.5,
}
DEFAULT_BODY_CAPACITY = 16.5
TABLE_ROW_CAPACITY = 10


def paginate_deck(deck: DeckIR) -> DeckIR:
    slides: list[SlideIR] = []
    for slide in deck.slides:
        slides.extend(_paginate_slide(slide))
    return DeckIR(slides=_dedupe_slide_ids(slides))


def _paginate_slide(slide: SlideIR) -> list[SlideIR]:
    if slide.table:
        return _paginate_table_slide(slide)
    if not slide.body or not slide.body.strip():
        return [slide]
    chunks = _chunk_body(slide.body, _body_capacity(slide.layout))
    if len(chunks) == 1:
        return [slide]
    result: list[SlideIR] = []
    for index, chunk in enumerate(chunks, start=1):
        update = {
            "body": chunk,
            "slide_id": f"{slide.slide_id}-{index}",
            "title": slide.title if index == 1 else f"{slide.title}（続き）",
        }
        if index > 1 and slide.layout == LayoutName.architecture_flow:
            update["layout"] = LayoutName.summary
            update["diagram"] = None
            update["slide_variant"] = TemplateSlideVariant.text
        result.append(slide.model_copy(update=update))
    return result


def _paginate_table_slide(slide: SlideIR) -> list[SlideIR]:
    table = slide.table
    if table is None or len(table.rows) <= TABLE_ROW_CAPACITY:
        return [slide]
    result: list[SlideIR] = []
    for index, start in enumerate(range(0, len(table.rows), TABLE_ROW_CAPACITY), start=1):
        rows = table.rows[start : start + TABLE_ROW_CAPACITY]
        update = {
            "slide_id": f"{slide.slide_id}-{index}",
            "title": slide.title if index == 1 else f"{slide.title}（続き）",
            "table": table.model_copy(update={"rows": rows}),
        }
        result.append(slide.model_copy(update=update))
    return result


def _body_capacity(layout: LayoutName) -> float:
    return BODY_CAPACITY_BY_LAYOUT.get(layout, DEFAULT_BODY_CAPACITY)


def _chunk_body(text: str, capacity: float) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return [""]

    groups = _split_oversized_groups(_top_level_groups(lines), capacity)
    total_units = sum(_group_units(group) for group in groups)
    chunk_count = max(1, min(len(groups), ceil(total_units / capacity)))
    chunks = _balanced_contiguous_chunks(groups, chunk_count)
    return ["\n".join(chunk) for chunk in chunks]


def _split_oversized_groups(groups: list[list[str]], capacity: float) -> list[list[str]]:
    result: list[list[str]] = []
    for group in groups:
        if _group_units(group) <= capacity:
            result.append(group)
            continue
        current: list[str] = []
        current_units = 0.0
        for line in group:
            line_units = _line_units(line)
            if current and current_units + line_units > capacity:
                result.append(current)
                current = []
                current_units = 0.0
            current.append(line)
            current_units += line_units
        if current:
            result.append(current)
    return result


def _balanced_contiguous_chunks(groups: list[list[str]], chunk_count: int) -> list[list[str]]:
    if chunk_count <= 1 or len(groups) <= 1:
        return [[line for group in groups for line in group]]

    best: list[list[str]] | None = None
    best_score: tuple[float, float, float] | None = None
    for boundaries in _boundary_combinations(len(groups) - 1, chunk_count - 1):
        starts = (0, *boundaries)
        ends = (*boundaries, len(groups))
        chunks = [[line for group in groups[start:end] for line in group] for start, end in zip(starts, ends)]
        units = [sum(_line_units(line) for line in chunk) for chunk in chunks]
        score = (max(units), max(units) - min(units), units[-1])
        if best_score is None or score < best_score:
            best_score = score
            best = chunks
    return best or [[line for group in groups for line in group]]


def _boundary_combinations(positions: int, count: int):
    if count == 0:
        yield ()
        return
    if count == 1:
        for position in range(1, positions + 1):
            yield (position,)
        return
    for first in range(1, positions - count + 2):
        for rest in _boundary_combinations(positions - first, count - 1):
            yield (first, *(first + item for item in rest))


def _group_units(group: list[str]) -> float:
    return sum(_line_units(line) for line in group)


def _top_level_groups(lines: list[str]) -> list[list[str]]:
    groups: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if _hierarchy_level(line) == 0 and current:
            groups.append(current)
            current = []
        current.append(line)
    if current:
        groups.append(current)
    return groups


def _line_units(line: str) -> float:
    level = _hierarchy_level(line)
    text = _strip_bullet_marker(line.strip())
    wrap_units = max(1, (len(text) + _wrap_width(level) - 1) // _wrap_width(level))
    if level == 0:
        return 1.75 * wrap_units
    return 1.1 * wrap_units


def _wrap_width(level: int) -> int:
    return max(18, 42 - level * 5)


def _hierarchy_level(raw_line: str) -> int:
    stripped = raw_line.lstrip()
    indent = len(raw_line) - len(stripped)
    marker_level = 1 if stripped.startswith(("・", "-", "*")) else 0
    return min(4, max(marker_level, indent // 2))


def _strip_bullet_marker(stripped: str) -> str:
    if stripped.startswith(("・", "-", "*")):
        return stripped[1:].strip()
    return stripped


def _dedupe_slide_ids(slides: list[SlideIR]) -> list[SlideIR]:
    counts: dict[str, int] = {}
    result: list[SlideIR] = []
    for slide in slides:
        count = counts.get(slide.slide_id, 0)
        counts[slide.slide_id] = count + 1
        if count == 0:
            result.append(slide)
        else:
            result.append(slide.model_copy(update={"slide_id": f"{slide.slide_id}-{count + 1}"}))
    return result
