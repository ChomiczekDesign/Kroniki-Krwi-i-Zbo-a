from pathlib import Path
import base64
import re
import shutil
from urllib.parse import unquote_to_bytes

SRC_DIR = Path("wiki")
OUT_DIR = Path("wiki_build")
CSS_SOURCE = Path(".github/assets/StarWarsDice.css")
FONT_PATH = "/.github/assets/EotE_Symbol-Regular_v1.otf"

# Kanoniczne nazwy tagów obsługiwanych przez skrypt
SUPPORTED_TAGS = [
    "Boost",
    "Setback",
    "Ability",
    "Difficulty",
    "Proficiency",
    "Challenge",
    "Force",
    "Success",
    "Failure",
    "Advantage",
    "Threat",
    "Triumph",
    "Despair",
    "LightDark",
]

# Aliasy wpisywane w markdownzie
ALIASES = {
    "boost": "Boost",
    "setback": "Setback",
    "ability": "Ability",
    "difficulty": "Difficulty",
    "proficiency": "Proficiency",
    "challenge": "Challenge",
    "force": "Force",
    "success": "Success",
    "failure": "Failure",
    "advantage": "Advantage",
    "threat": "Threat",
    "triumph": "Triumph",
    "despair": "Despair",
    "lightdark": "LightDark",
    "light-dark": "LightDark",
    "lightdarkside": "LightDark",
}

# Symbole, które mają zostać jako inline SVG z currentColor
CURRENT_COLOR_TAGS = {
    "Success",
    "Failure",
    "Advantage",
    "Threat",
    "Triumph",
    "Despair",
    "LightDark",
}

# Kości, które renderujemy fontem
DICE_TAG_TO_GLYPH = {
    "boost": ("b", "dice-boost"),          # pełny kwadrat
    "setback": ("B", "dice-setback"),      # pusty kwadrat
    "ability": ("d", "dice-ability"),      # pełny romb
    "difficulty": ("D", "dice-difficulty"),# pusty romb
    "proficiency": ("c", "dice-proficiency"), # pełny hex
    "challenge": ("C", "dice-challenge"),     # pusty hex
    "force": ("w", "dice-force"),          # symbol mocy z fonta
}

# Znajdź wszystkie #Tagi
TAG_PATTERN = re.compile(r'(?<![\w/])#([A-Za-z][A-Za-z\-]*)(?![\w-])')

# Wyciąga data:image/svg+xml... z CSS
CSS_ICON_PATTERN = re.compile(
    r'href\^\="#(?P<name>[A-Za-z]+)"[\s\S]*?content:\s*url\("(?P<data>data:image/svg\+xml(?:;base64)?,[^"]+)"\);',
    re.MULTILINE,
)

INJECTED_STYLE = f"""
<style>
@font-face {{
  font-family: 'EotE Symbols';
  src: url('{FONT_PATH}') format('opentype');
  font-weight: normal;
  font-style: normal;
}}

.dice-font {{
  font-family: 'EotE Symbols', sans-serif;
  display: inline-block;
  line-height: 1;
  vertical-align: -0.08em;
  font-weight: normal;
  font-style: normal;
}}

.dice-boost {{
  color: #56A7E9;
  font-size: 1.05em;
}}

.dice-setback {{
  color: #f5f5f5;
  font-size: 1.05em;
  text-shadow:
    0.03em 0 0 currentColor,
    -0.03em 0 0 currentColor,
    0 0.03em 0 currentColor,
    0 -0.03em 0 currentColor;
}}

.dice-ability {{
  color: #44D433;
  font-size: 1.08em;
}}

.dice-difficulty {{
  color: #A06BFF;
  font-size: 1.08em;
  text-shadow:
    0.02em 0 0 currentColor,
    -0.02em 0 0 currentColor,
    0 0.02em 0 currentColor,
    0 -0.02em 0 currentColor;
}}

.dice-proficiency {{
  color: #FFF041;
  font-size: 1.15em;
}}

.dice-challenge {{
  color: #FF4A4A;
  font-size: 1.15em;
  text-shadow:
    0.02em 0 0 currentColor,
    -0.02em 0 0 currentColor,
    0 0.02em 0 currentColor,
    0 -0.02em 0 currentColor;
}}

.dice-force {{
  color: #f5f5f5;
  font-size: 1.15em;
  text-shadow:
    0.03em 0 0 currentColor,
    -0.03em 0 0 currentColor,
    0 0.03em 0 currentColor,
    0 -0.03em 0 currentColor;
}}

.dice-inline {{
  display: inline-block;
  width: 0.95em;
  height: 0.95em;
  vertical-align: -0.12em;
  color: inherit;
  overflow: visible;
}}
</style>
""".strip()


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


def normalize_svg_markup(svg: str) -> str:
    svg = re.sub(r'^\s*<\?xml[^>]*>\s*', '', svg, flags=re.IGNORECASE)
    svg = re.sub(r'^\s*<!DOCTYPE[^>]*>\s*', '', svg, flags=re.IGNORECASE)
    svg = re.sub(r'[\r\n\t]+', ' ', svg)
    svg = re.sub(r'>\s+<', '><', svg)
    svg = re.sub(r'\s{2,}', ' ', svg)
    return svg.strip()


def replace_black_with_current_color(svg: str) -> str:
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

    svg = re.sub(rf'(?i)(fill\s*:\s*){color_pattern}', r'\1currentColor', svg)
    svg = re.sub(rf'(?i)(stroke\s*:\s*){color_pattern}', r'\1currentColor', svg)

    return svg


def append_or_set_attr(attr_string: str, attr_name: str, attr_value: str) -> str:
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

    if re.search(rf'\b{re.escape(attr_name)}\s*=', attr_string, flags=re.IGNORECASE):
        return re.sub(
            rf'\b{re.escape(attr_name)}\s*=\s*"[^"]*"',
            f'{attr_name}="{attr_value}"',
            attr_string,
            count=1,
            flags=re.IGNORECASE,
        )

    return attr_string + f' {attr_name}="{attr_value}"'


def transform_svg_root(
    svg: str,
    tag_name: str,
    *,
    class_name: str,
    style: str,
    force_current_color_fill: bool = False,
) -> str:
    match = re.search(r'<svg\b([^>]*)>', svg, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Nie znaleziono znacznika <svg> dla {tag_name}")

    attrs = match.group(1)

    attrs = re.sub(r'\swidth\s*=\s*"[^"]*"', '', attrs, flags=re.IGNORECASE)
    attrs = re.sub(r"\swidth\s*=\s*'[^']*'", '', attrs, flags=re.IGNORECASE)
    attrs = re.sub(r'\sheight\s*=\s*"[^"]*"', '', attrs, flags=re.IGNORECASE)
    attrs = re.sub(r"\sheight\s*=\s*'[^']*'", '', attrs, flags=re.IGNORECASE)

    attrs = append_or_set_attr(attrs, "class", class_name)
    attrs = append_or_set_attr(attrs, "style", style)
    attrs = append_or_set_attr(attrs, "role", "img")
    attrs = append_or_set_attr(attrs, "aria-label", tag_name)
    attrs = append_or_set_attr(attrs, "focusable", "false")
    attrs = append_or_set_attr(attrs, "preserveAspectRatio", "xMidYMid meet")

    if force_current_color_fill:
        attrs = append_or_set_attr(attrs, "fill", "currentColor")
        attrs = append_or_set_attr(attrs, "stroke", "currentColor")

    new_svg_tag = f"<svg{attrs}>"
    svg = svg[:match.start()] + new_svg_tag + svg[match.end():]
    return svg


def canonicalize_tag(raw_tag: str) -> str | None:
    return ALIASES.get(raw_tag.lower())


def build_symbol_html(tag_name: str, data_uri: str) -> str:
    svg = decode_data_uri_to_svg(data_uri)
    svg = normalize_svg_markup(svg)
    svg = replace_black_with_current_color(svg)

    svg = transform_svg_root(
        svg,
        tag_name,
        class_name=f"dice-inline dice-symbol dice-{tag_name.lower()}",
        style="display:inline-block;width:0.95em;height:0.95em;vertical-align:-0.12em;color:inherit;overflow:visible;",
        force_current_color_fill=True,
    )

    return svg


def build_font_die_html(tag_name_lower: str) -> str:
    glyph, css_class = DICE_TAG_TO_GLYPH[tag_name_lower]
    return f'<span class="dice-font {css_class}" title="{tag_name_lower}">{glyph}</span>'


def build_replacement(tag_name: str, icon_map: dict[str, str]) -> str:
    lower = tag_name.lower()

    if lower in DICE_TAG_TO_GLYPH:
        return build_font_die_html(lower)

    if tag_name in CURRENT_COLOR_TAGS:
        data_uri = icon_map.get(tag_name)
        if data_uri:
            return build_symbol_html(tag_name, data_uri)

    return f"#{tag_name}"


def replace_tags(text: str, icon_map: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        raw_tag = match.group(1)  # bez #
        canonical = canonicalize_tag(raw_tag)
        if not canonical:
            return match.group(0)

        return build_replacement(canonical, icon_map)

    return TAG_PATTERN.sub(repl, text)


def inject_style_block(text: str) -> str:
    if "@font-face" in text or "dice-font" in text:
        return text
    return INJECTED_STYLE + "\n\n" + text


def main() -> None:
    if not CSS_SOURCE.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku CSS: {CSS_SOURCE}")

    css_text = CSS_SOURCE.read_text(encoding="utf-8")
    icon_map = extract_icons_from_css(css_text)

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    shutil.copytree(SRC_DIR, OUT_DIR)

    for path in OUT_DIR.rglob("*.md"):
        original = path.read_text(encoding="utf-8")
        updated = replace_tags(original, icon_map)
        updated = inject_style_block(updated)
        path.write_text(updated, encoding="utf-8")

    print(f"[OK] Zbudowano przetworzone markdowny w: {OUT_DIR}")


if __name__ == "__main__":
    main()
