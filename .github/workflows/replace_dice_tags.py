from pathlib import Path
import base64
import html
import re
import shutil
from urllib.parse import unquote_to_bytes

SRC_DIR = Path("wiki")
OUT_DIR = Path("wiki_build")
CSS_SOURCE = Path(".github/assets/StarWarsDice.css")

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

# Te tagi będą renderowane jako inline SVG dziedziczące kolor tekstu.
CURRENT_COLOR_TAGS = {
    "Success",
    "Failure",
    "Advantage",
    "Threat",
    "Triumph",
    "Despair",
}

TAG_PATTERN = re.compile(
    r'(?<![\w/])(' + '|'.join(re.escape(f"#{tag}") for tag in SUPPORTED_TAGS) + r')(?![\w-])'
)

CSS_ICON_PATTERN = re.compile(
    r'href\^\="#(?P<name>[A-Za-z]+)"[\s\S]*?content:\s*url\("(?P<data>data:image/svg\+xml(?:;base64)?,[^"]+)"\);',
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


def decode_data_uri_to_svg(data_uri: str) -> str:
    if not data_uri.startswith("data:image/svg+xml"):
        raise ValueError("Nieobsługiwany data URI: " + data_uri[:64])

    header, payload = data_uri.split(",", 1)

    if ";base64" in header:
        raw = base64.b64decode(payload)
    else:
        raw = unquote_to_bytes(payload)

    return raw.decode("utf-8")


def replace_black_with_current_color(svg: str) -> str:
    # Zamiana typowych czarnych fill/stroke na currentColor
    color_pattern = r'(?:#000000|#000|black|rgb\(\s*0\s*,\s*0\s*,\s*0\s*\)|rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*1(?:\.0+)?\s*\))'

    for attr in ("fill", "stroke"):
        svg = re.sub(
            rf'({attr}\s*=\s*")({color_pattern})(")',
            rf'\1currentColor\3',
            svg,
            flags=re.IGNORECASE,
        )
        svg = re.sub(
            rf"({attr}\s*=\s*')({color_pattern})(')",
            rf"\1currentColor\3",
            svg,
            flags=re.IGNORECASE,
        )

    # Zamiana w stylach inline typu style="fill:#000;stroke:black"
    svg = re.sub(
        rf'(?i)(fill\s*:\s*){color_pattern}',
        r'\1currentColor',
        svg,
    )
    svg = re.sub(
        rf'(?i)(stroke\s*:\s*){color_pattern}',
        r'\1currentColor',
        svg,
    )

    return svg


def append_or_set_attr(attr_string: str, attr_name: str, attr_value: str) -> str:
    # class
    if attr_name == "class":
        m = re.search(r'\bclass\s*=\s*"([^"]*)"', attr_string, flags=re.IGNORECASE)
        if m:
            existing = m.group(1).strip()
            combined = (existing + " " + attr_value).strip()
            return re.sub(
                r'\bclass\s*=\s*"([^"]*)"',
                f'class="{combined}"',
                attr_string,
                count=1,
                flags=re.IGNORECASE,
            )
        return attr_string + f' class="{attr_value}"'

    # style
    if attr_name == "style":
        m = re.search(r'\bstyle\s*=\s*"([^"]*)"', attr_string, flags=re.IGNORECASE)
        if m:
            existing = m.group(1).strip()
            sep = ";" if existing and not existing.endswith(";") else ""
            combined = f"{existing}{sep}{attr_value}"
            return re.sub(
                r'\bstyle\s*=\s*"([^"]*)"',
                f'style="{combined}"',
                attr_string,
                count=1,
                flags=re.IGNORECASE,
            )
        return attr_string + f' style="{attr_value}"'

    # generic
    if re.search(rf'\b{re.escape(attr_name)}\s*=', attr_string, flags=re.IGNORECASE):
        return re.sub(
            rf'\b{re.escape(attr_name)}\s*=\s*"[^"]*"',
            f'{attr_name}="{attr_value}"',
            attr_string,
            count=1,
            flags=re.IGNORECASE,
        )

    return attr_string + f' {attr_name}="{attr_value}"'


def transform_svg_root(svg: str, tag_name: str) -> str:
    svg = re.sub(r'^\s*<\?xml[^>]*>\s*', '', svg, flags=re.IGNORECASE)
    svg = re.sub(r'^\s*<!DOCTYPE[^>]*>\s*', '', svg, flags=re.IGNORECASE)
    svg = svg.strip()

    match = re.search(r'<svg\b([^>]*)>', svg, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Nie znaleziono znacznika <svg> dla {tag_name}")

    attrs = match.group(1)

    # Usuń width/height z oryginału, żeby nasze 1em było pewne
    attrs = re.sub(r'\swidth\s*=\s*"[^"]*"', '', attrs, flags=re.IGNORECASE)
    attrs = re.sub(r"\swidth\s*=\s*'[^']*'", '', attrs, flags=re.IGNORECASE)
    attrs = re.sub(r'\sheight\s*=\s*"[^"]*"', '', attrs, flags=re.IGNORECASE)
    attrs = re.sub(r"\sheight\s*=\s*'[^']*'", '', attrs, flags=re.IGNORECASE)

    attrs = append_or_set_attr(attrs, "class", f"dice-inline dice-{tag_name.lower()}")
    attrs = append_or_set_attr(
        attrs,
        "style",
        "display:inline-block;width:1em;height:1em;vertical-align:-0.12em;color:inherit;"
    )
    attrs = append_or_set_attr(attrs, "role", "img")
    attrs = append_or_set_attr(attrs, "aria-label", tag_name)
    attrs = append_or_set_attr(attrs, "focusable", "false")
    attrs = append_or_set_attr(attrs, "fill", "currentColor")

    new_svg_tag = f"<svg{attrs}>"
    svg = svg[:match.start()] + new_svg_tag + svg[match.end():]

    return svg


def build_inline_svg_html(tag_name: str, data_uri: str) -> str:
    svg = decode_data_uri_to_svg(data_uri)
    svg = replace_black_with_current_color(svg)
    svg = transform_svg_root(svg, tag_name)
    return svg


def build_img_html(tag_name: str, data_uri: str) -> str:
    safe_name = html.escape(tag_name, quote=True)
    safe_uri = html.escape(data_uri, quote=True)
    return (
        f'<img class="dice-inline dice-{tag_name.lower()}" '
        f'src="{safe_uri}" alt="{safe_name}" title="{safe_name}" '
        f'style="display:inline-block;width:1em;height:1em;vertical-align:-0.12em;" />'
    )


def build_replacement(tag_name: str, data_uri: str) -> str:
    if tag_name in CURRENT_COLOR_TAGS:
        return build_inline_svg_html(tag_name, data_uri)
    return build_img_html(tag_name, data_uri)


def replace_tags(text: str, icon_map: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        full_tag = match.group(1)   # np. "#Advantage"
        tag_name = full_tag[1:]     # np. "Advantage"
        data_uri = icon_map.get(tag_name)
        if not data_uri:
            return full_tag
        return build_replacement(tag_name, data_uri)

    return TAG_PATTERN.sub(repl, text)


def main() -> None:
    if not CSS_SOURCE.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku CSS: {CSS_SOURCE}")

    css_text = CSS_SOURCE.read_text(encoding="utf-8")
    icon_map = extract_icons_from_css(css_text)

    missing = [tag for tag in SUPPORTED_TAGS if tag not in icon_map]
    if missing:
        raise RuntimeError(
            "Nie udało się wyciągnąć ikon dla tagów: " + ", ".join(missing)
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
