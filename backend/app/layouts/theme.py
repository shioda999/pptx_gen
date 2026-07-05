from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    background: str
    foreground: str
    muted: str
    accent: str
    accent_dark: str
    panel: str
    line: str


THEMES = {
    "modern-tech": Theme(
        background="F7F9FB",
        foreground="172033",
        muted="526071",
        accent="2D8CFF",
        accent_dark="125D9C",
        panel="FFFFFF",
        line="CAD3DF",
    ),
    "neutral": Theme(
        background="FFFFFF",
        foreground="1F2933",
        muted="667085",
        accent="0F766E",
        accent_dark="115E59",
        panel="F8FAFC",
        line="CBD5E1",
    ),
}


def get_theme(name: str) -> Theme:
    return THEMES[name]
