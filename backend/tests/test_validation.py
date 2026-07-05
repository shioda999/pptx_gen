import pytest
from pydantic import ValidationError

from app.schemas.slide import DiagramSpec, SlideIR, TableSpec


def test_table_column_mismatch_is_invalid():
    with pytest.raises(ValidationError):
        TableSpec(headers=["a", "b"], rows=[["only-one"]])


def test_diagram_edge_must_reference_existing_nodes():
    with pytest.raises(ValidationError):
        DiagramSpec(
            nodes=[{"id": "a", "label": "A"}],
            edges=[{"from": "a", "to": "missing"}],
        )


def test_architecture_flow_requires_diagram():
    with pytest.raises(ValidationError):
        SlideIR(slide_id="x", layout="architecture-flow", title="x")
