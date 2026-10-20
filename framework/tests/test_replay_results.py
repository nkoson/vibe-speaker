import importlib.util
from pathlib import Path
import sys
import pytest
TOOLS=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
from replay_results import file_references,replay_order


def test_change_closure_and_topological_order():
    graph={'box':set(),'fixed':set(),'source':{'box'},'board':{'source','fixed'},'system':{'source','board'},'room':{'system'}}
    order=replay_order(graph,['box'])
    assert set(order)=={'box','source','board','system','room'}
    assert order.index('source')<order.index('board')<order.index('system')<order.index('room')
    assert list(file_references({'steps':[{'parameters':{'ref':{'file':'one.json'}}},{'file':'@board'}]}))==['one.json']


def test_cycle_and_unknown_seed_are_reported():
    with pytest.raises(ValueError,match='cycle'):replay_order({'a':{'b'},'b':{'a'}},['a'])
    with pytest.raises(ValueError,match='unknown'):replay_order({'a':set()},['b'])
