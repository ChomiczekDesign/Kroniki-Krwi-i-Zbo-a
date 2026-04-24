from pathlib import Path
import html
import re
import shutil

SRC_DIR = Path("wiki")
OUT_DIR = Path("wiki_build")
CSS_SOURCE = Path(".github/assets/StarWarsDice.css")

# Tagi, które chcemy wspierać w markdownzie
SUPPORTED_TAGS = [
    "Boost",
    "Setback",
    "Ability",
    "Difficulty",
    "Proficiency",
    "Challenge",
    "Success",
    "Failure",
    "Advantage",
    "Threat",
    "Triumph",
    "Despair",
]

TAG_PATTERN = re.compile(
    r'(?<![\w/])(' + '|'.join(re.escape(f"#{tag}") for tag in SUPPORTED_TAGS) + r')(?![\w-])'
)

# Wyciąga data URI z bloków CSS typu:
# body a.tag.tag[href^="#Boost"] ... content: url("data:image/svg+xml;base64,...");
CSS_ICON_PATTERN = re.compile(
    r'href\^\="#(?P<name>[A-Za-z]+)"[\s\S]*?content:\s*url\("(?P<data>data:image/svg\+xml;base64,[^"]+)"\);',
    re.MULTILINE,
)


def extract_icons_from_css(css_text: str) -> dict[str, str]:
    icons: dict[str, str] = {}
    for match in CSS_ICON_PATTERN.finditer(css_text):
        name = match.group("name")
        data_uri = match.group("data")
        if name in SUPPORTED_TAGS and name not in icons:
            icons[name] = data_uri
    return icons


def build_img_html(tag_name: str, data_uri: str) -> str:
    safe_name = html.escape(tag_name, quote=True)
    safe_uri = html.escape(data_uri, quote=True)
    return (
        f'<img class="dice-inline dice-{tag_name.lower()}" '
        f'src="{safe_uri}" alt="{safe_name}" title="{safe_name}" '
        f'style="display:inline-block;width:1em;height:1em;vertical-align:-0.12em;" />'
    )


def replace_tags(text: str, icon_map: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        full_tag = match.group(1)      # np. "#Advantage"
        tag_name = full_tag[1:]        # np. "Advantage"
        data_uri = icon_map.get(tag_name)
        if not data_uri:
            return full_tag
        return build_img_html(tag_name, data_uri)

    return TAG_PATTERN.sub(repl, text)


def main() -> None:
    if not CSS_SOURCE.exists():
        raise FileNotFoundError(
            f"Nie znaleziono pliku CSS z symbolami: {CSS_SOURCE}"
        )

    css_text = CSS_SOURCE.read_text(encoding="utf-8")
    icon_map = extract_icons_from_css(css_text)

    missing = [tag for tag in SUPPORTED_TAGS if tag not in icon_map]
    if missing:
        raise RuntimeError(
            "Nie udało się wyciągnąć symboli dla tagów: " + ", ".join(missing)
        )

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    shutil.copytree(SRC_DIR, OUT_DIR)

    for path in OUT_DIR.rglob("*.md"):
        original = path.read_text(encoding="utf-8")
        updated = replace_tags(original, icon_map)
        path.write_text(updated, encoding="utf-8")

    print(f"[OK] Zbudowano przetworzone markdowny w: {OUT_DIR}")


if __name__ == "__main__":
    main()
