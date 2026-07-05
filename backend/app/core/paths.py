from pathlib import Path

from app.core.config import Settings, get_settings


class PathSecurityError(ValueError):
    pass


def resolve_inside_root(path_value: str | Path, root: Path) -> Path:
    root = root.resolve()
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    if resolved != root and root not in resolved.parents:
        raise PathSecurityError(f"path escapes allowed root: {path_value}")
    return resolved


def resolve_project_path(path_value: str | Path, settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = settings.project_root / candidate
    resolved = candidate.resolve()
    allowed = tuple(root.resolve() for root in settings.allowed_roots)
    if not any(resolved == root or root in resolved.parents for root in allowed):
        raise PathSecurityError(f"path escapes allowed directories: {path_value}")
    return resolved


def ensure_output_path(filename: str, settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    safe_name = Path(filename).name
    if not safe_name:
        raise PathSecurityError("output filename is required")
    return resolve_inside_root(safe_name, settings.outputs_dir)
