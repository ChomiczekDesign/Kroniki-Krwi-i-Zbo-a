from pathlib import Path
import re
import shutil

SRC_DIR = Path("wiki")
OUT_DIR = Path("wiki_build")

# Mapowanie tagów na proste inline znaczniki.
# Na start używam tekstowych fallbacków, żeby sprawdzić pipeline.
# Potem możemy tu podmienić wartości na prawdziwe SVG inline.
REPLACEMENTS = {
    "#Boost": '<span class="dice-inline" title="Boost">🟦</span>',
    "#Setback": '<span class="dice-inline" title="Setback">⬛</span>',
    "#Ability": '<span class="dice-inline" title="Ability">🟩</span>',
    "#Difficulty": '<span class="dice-inline" title="Difficulty">🟪</span>',
    "#Proficiency": '<span class="dice-inline" title="Proficiency">🟨</span>',
    "#Challenge": '<span class="dice-inline" title="Challenge">🟥</span>',
    "#Success": '<span class="dice-inline" title="Success">✦</span>',
    "#Failure": '<span class="dice-inline" title="Failure">✖</span>',
    "#Advantage": '<span class="dice-inline" title="Advantage">◆</span>',
    "#Threat": '<span class="dice-inline" title="Threat">▲</span>',
    "#Triumph": '<span class="dice-inline" title="Triumph">✹</span>',
    "#Despair": '<span class="dice-inline" title="Despair">☠</span>',
}

TAG_PATTERN = re.compile(
    r'(?<![\w/])(' + '|'.join(re.escape(tag) for tag in REPLACEMENTS.keys()) + r')(?![\w-])'
)

def replace_tags(text: str) -> str:
    return TAG_PATTERN.sub(lambda m: REPLACEMENTS[m.group(1)], text)

def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    shutil.copytree(SRC_DIR, OUT_DIR)

    for path in OUT_DIR.rglob("*.md"):
        original = path.read_text(encoding="utf-8")
        updated = replace_tags(original)
        path.write_text(updated, encoding="utf-8")

    print(f"[OK] Built processed markdown in {OUT_DIR}")

if __name__ == "__main__":
    main()
