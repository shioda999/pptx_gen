from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    project_root: Path = Path(__file__).resolve().parents[3]
    input_dir: Path | None = None
    templates_dir: Path | None = None
    workspaces_dir: Path | None = None
    outputs_dir: Path | None = None
    rendered_dir: Path | None = None
    max_image_bytes: int = 10 * 1024 * 1024

    def model_post_init(self, __context: object) -> None:
        object.__setattr__(self, "input_dir", self.project_root / "input")
        object.__setattr__(self, "templates_dir", self.project_root / "templates")
        object.__setattr__(self, "workspaces_dir", self.project_root / "workspaces")
        object.__setattr__(self, "outputs_dir", self.project_root / "outputs")
        object.__setattr__(self, "rendered_dir", self.project_root / "rendered")

    @property
    def allowed_roots(self) -> tuple[Path, ...]:
        return (
            self.project_root,
            self.input_dir,
            self.templates_dir,
            self.workspaces_dir,
            self.outputs_dir,
            self.rendered_dir,
        )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    for directory in (
        settings.input_dir,
        settings.templates_dir,
        settings.workspaces_dir,
        settings.outputs_dir,
        settings.rendered_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)
    return settings
