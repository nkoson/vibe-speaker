"""schematic.py must emit a board_nodal netlist whose component ids are unique.

A parallel capacitor bank or a series resistor array is one element with several leaves; before the
fix every leaf inherited one id and board_nodal refused the file schematic.py had just written.
"""
import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location("schematic", TOOLS / "schematic.py")
schematic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schematic)

SECTIONS = [{
    "name": "mf", "polarity": 1, "wire_loop_ohm": 0.05,
    "load": {"kind": "resistive", "r_ohm": 6.5},
    "elements": [
        {"id": "C2", "position": "series", "type": "parallel",
         "parts": [{"type": "C", "value_uf": 22}, {"type": "C", "value_uf": 2.2}, {"type": "C", "value_uf": 1.5}]},
        {"id": "Rs2", "position": "series", "type": "series",
         "parts": [{"type": "R", "value_ohm": 3.3}, {"type": "R", "value_ohm": 3.3}, {"type": "R", "value_ohm": 3.3}]},
        {"id": "Rp2", "position": "shunt", "type": "R", "value_ohm": 15, "rating": {"power_w": 25}},
    ]}]


def test_every_component_id_is_unique():
    board, connections = schematic.netlist(SECTIONS)
    ids = [c["id"] for c in board["components"]]
    assert len(ids) == len(set(ids)), sorted(ids)


def test_composite_leaves_keep_their_reference_with_a_suffix():
    board, connections = schematic.netlist(SECTIONS)
    ids = {c["id"] for c in board["components"]}
    assert {"C2a", "C2b", "C2c"} <= ids, sorted(ids)
    assert {"Rs2a", "Rs2b", "Rs2c"} <= ids, sorted(ids)
    assert "Rp2" in ids


def test_the_connection_table_uses_the_same_ids():
    board, connections = schematic.netlist(SECTIONS)
    component_ids = {c["id"] for c in board["components"]}
    table_ids = {row["id"] for row in connections}
    assert table_ids <= component_ids, sorted(table_ids - component_ids)
    assert len({row["id"] for row in connections}) == len(connections)


def test_a_composite_label_puts_one_member_per_line():
    bank = SECTIONS[0]["elements"][0]
    label = schematic._label_block(bank)
    lines = label.split("\n")
    assert len(lines) == 1 + len(bank["parts"]), label
    assert lines[0].startswith("C2")
    # a single run-on line is what used to overlap the neighbouring element's label
    assert max(len(line) for line in lines) < len(" ∥ ".join(lines[1:]))


def test_a_leaf_label_still_carries_its_full_specification():
    leaf = SECTIONS[0]["elements"][2]
    label = schematic._label_block(leaf)
    assert "15 Ω" in label and "25 W" in label


def test_the_shipped_tool_example_produces_a_usable_board_netlist():
    """example_crossover.json is the file the docstring points a reader at; keep it working."""
    import json
    example = json.loads((TOOLS / "example_crossover.json").read_text())
    board, connections = schematic.netlist(example["sections"], base_dir=str(TOOLS))
    ids = [c["id"] for c in board["components"]]
    assert len(ids) == len(set(ids)), sorted(ids)
    assert len(board["loads"]) == len(example["sections"])
    # the banks and arrays the example exists to cover
    assert {"C1a", "C1b", "C2a", "C2b", "C2c", "Rs2a", "Rs2b", "Rs2c"} <= set(ids), sorted(ids)
