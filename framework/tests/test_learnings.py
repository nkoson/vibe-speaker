"""Well-formedness of the learnings directory: frontmatter, sections and index coverage."""
import re
from pathlib import Path

LEARNINGS = Path(__file__).resolve().parents[1] / "learnings"
REQUIRED_KEYS = ("id", "date", "project", "phase", "confidence", "applies_when", "tags")
PHASES = {"validation", "research", "design", "evaluation", "selection", "documentation", "process"}
SECTIONS = ("## Observation", "## Why it mattered", "## Advice", "## Evidence")


def learning_files():
    return sorted(p for p in LEARNINGS.glob("*.md") if p.name not in ("README.md", "INDEX.md"))


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, "missing frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def test_learning_files_are_well_formed():
    files = learning_files()
    assert files, "no learnings found"
    for path in files:
        text = path.read_text()
        fields = frontmatter(text)
        for key in REQUIRED_KEYS:
            assert fields.get(key), f"{path.name}: missing {key}"
        assert fields["id"] == path.stem, f"{path.name}: id must equal the file name"
        assert fields["phase"] in PHASES, f"{path.name}: unknown phase {fields['phase']}"
        assert fields["confidence"] in {"low", "medium", "high"}, f"{path.name}: bad confidence"
        for section in SECTIONS:
            assert section in text, f"{path.name}: missing section {section}"


def test_index_lists_every_learning_once():
    index = (LEARNINGS / "INDEX.md").read_text()
    for path in learning_files():
        assert index.count(f"({path.name})") == 1, f"INDEX.md must list {path.name} exactly once"
    listed = set(re.findall(r"\(([a-z0-9-]+\.md)\)", index))
    assert listed == {p.name for p in learning_files()}, "INDEX.md lists a file that does not exist"


def test_advice_is_not_phrased_as_absolute_rules():
    for path in learning_files():
        advice = path.read_text().split("## Advice", 1)[1].split("## Evidence", 1)[0].lower()
        for word in (" always ", " never ", " must "):
            assert word not in advice, f"{path.name}: advice contains '{word.strip()}'; phrase it as a consideration"
