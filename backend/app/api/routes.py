from fastapi import APIRouter, HTTPException, status

from app.schemas.api import (
    CreateDeckRequest,
    CreateDeckResponse,
    GenericTemplateRequest,
    RenderRequest,
    ValidateRequest,
    ValidateResponse,
)
from app.services.deck_service import DeckService
from app.template_editor.pptx_template import TemplatePptxEditor

router = APIRouter()


@router.post("/create-deck", response_model=CreateDeckResponse)
def create_deck(request: CreateDeckRequest) -> CreateDeckResponse:
    try:
        return DeckService().create_deck(request)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/validate", response_model=ValidateResponse)
def validate(request: ValidateRequest) -> ValidateResponse:
    return DeckService().validate(request)


@router.post("/render")
def render(request: RenderRequest) -> dict[str, str]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="rendering to PDF/PNG is planned for Phase 2",
    )


@router.post("/inspect-presentation")
def inspect_presentation(request: GenericTemplateRequest) -> dict:
    try:
        path = request.pptx_path or request.template_path
        if not path:
            raise ValueError("pptx_path or template_path is required")
        return TemplatePptxEditor().inspect(path)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/update-slide")
def update_slide(request: GenericTemplateRequest) -> dict:
    try:
        if not request.pptx_path:
            raise ValueError("pptx_path is required")
        result = TemplatePptxEditor().update_shapes(
            request.pptx_path,
            request.output_filename,
            request.slide_key,
            request.slide_index,
            request.payload,
        )
        return {"pptx_path": str(result.pptx_path), "slide_count": result.slide_count, "warnings": result.warnings}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/set-table")
def set_table(request: GenericTemplateRequest) -> dict:
    try:
        if not request.pptx_path or not request.shape_name:
            raise ValueError("pptx_path and shape_name are required")
        from app.schemas.slide import TableSpec

        result = TemplatePptxEditor().set_table(
            request.pptx_path,
            request.output_filename,
            request.slide_key,
            request.slide_index,
            request.shape_name,
            TableSpec.model_validate(request.payload),
        )
        return {"pptx_path": str(result.pptx_path), "slide_count": result.slide_count, "warnings": result.warnings}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/set-image")
def set_image(request: GenericTemplateRequest) -> dict:
    try:
        if not request.pptx_path or not request.shape_name:
            raise ValueError("pptx_path and shape_name are required")
        image_path = request.payload.get("path")
        if not image_path:
            raise ValueError("payload.path is required")
        result = TemplatePptxEditor().set_image(
            request.pptx_path,
            request.output_filename,
            request.slide_key,
            request.slide_index,
            request.shape_name,
            str(image_path),
        )
        return {"pptx_path": str(result.pptx_path), "slide_count": result.slide_count, "warnings": result.warnings}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/generate-speaker-notes")
def generate_speaker_notes(request: GenericTemplateRequest) -> dict:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PowerPoint notes-pane writing is reserved for the COM editor; /create-deck already writes speaker_notes.md",
    )


@router.post("/insert-slide")
def insert_slide(request: GenericTemplateRequest) -> dict[str, str]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="template slide insertion is reserved for the COM editor",
    )
