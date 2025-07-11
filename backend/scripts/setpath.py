import os
import sys
from pathlib import Path
from typing import Literal

__all__ = ['setpath']


def _set_cwd():
    if (Path.cwd() / '.github' / 'workflows').exists():
        return
    candidate = Path(__file__).parent  # Start at this dir
    while not (candidate / '.github' / 'workflows').exists():
        if candidate.parent == candidate:
            raise FileNotFoundError("Cannot find arcanar_game root directory")
        candidate = candidate.parent
    os.chdir(candidate)


def _setup_sys_path():
    """Ensure the root arcanar_game folder is in sys.path, requires cwd to be
    set to the arcanar_game root dir (e.g. via ``_set_cwd``)"""
    if any(Path(p).resolve() == Path.cwd().resolve() for p in sys.path):
        return  # Already present
    sys.path.append(str(Path.cwd()))


def _check_env():
    try:
        import websockets.sync.server as _
        return
    except ImportError:
        if (activator_path := Path('./venv/Scripts/activate_this.py')).exists():
            print("Activating venv inplace")
            import runpy
            runpy.run_path(str(activator_path))
            return
        raise


def setpath() -> Literal[True]:
    _set_cwd()
    _setup_sys_path()
    _check_env()
    return True
