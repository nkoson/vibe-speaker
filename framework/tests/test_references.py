"""Well-formedness of the references directory: frontmatter, sources and the links that point at it."""
import re
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
REFERENCES = HARNESS / "references"
REQUIRED_KEYS = ("id", "applies_when", "updated")


def reference_files():
    return sorted(p for p in REFERENCES.glob("*.md") if p.name != "README.md")


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, "missing frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def test_reference_files_are_well_formed():
    files = reference_files()
    assert files, "no references found"
    for path in files:
        text = path.read_text()
        fields = frontmatter(text)
        for key in REQUIRED_KEYS:
            assert fields.get(key), f"{path.name}: missing {key}"
        assert fields["id"] == path.stem, f"{path.name}: id must equal the file name"
        assert "## Sources" in text, f"{path.name}: missing a Sources section"
        sources = [line for line in text.split("## Sources", 1)[1].splitlines() if line.startswith("- ")]
        assert len(sources) >= 3, f"{path.name}: a reference names at least three sources"


def test_readme_lists_every_reference_once():
    readme = (REFERENCES / "README.md").read_text()
    for path in reference_files():
        assert readme.count(f"({path.name})") == 1, f"references/README.md must list {path.name} exactly once"
    listed = set(re.findall(r"\(([a-z0-9-]+\.md)\)", readme))
    assert listed == {p.name for p in reference_files()}, "references/README.md lists a file that does not exist"


def test_links_to_references_resolve():
    targets = {f"framework/references/{p.name}" for p in reference_files()} | {"framework/references/README.md"}
    for skill in sorted((HARNESS / "skills").glob("*/SKILL.md")):
        for link in re.findall(r"framework/references/[a-zA-Z0-9_./-]*\.md", skill.read_text()):
            assert link in targets, f"{skill.parent.name}: link to missing reference {link}"
