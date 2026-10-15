"""Load standalone compute functions without coupling their command-line state."""
import importlib.util
from pathlib import Path
from functools import lru_cache
from . import cli

@lru_cache(None)
def module(name):
    root=Path(__file__).resolve().parents[1]
    if Path(name).name!=name:raise cli.InputError("app name is not a folder name")
    path=root/name/"run.py"
    if not path.exists():raise cli.InputError(f"unknown app {name}")
    spec=importlib.util.spec_from_file_location("speaker_app_"+name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value
