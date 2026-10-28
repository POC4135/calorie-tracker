import importlib.util
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPT = os.path.join(ROOT, "shared", "scripts", "macros.py")
DATA = os.path.join(ROOT, "data")


def _load():
    spec = importlib.util.spec_from_file_location("katori_macros", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["katori_macros"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def m():
    os.environ["KATORI_DATA_DIR"] = DATA
    return _load()


@pytest.fixture(scope="session")
def foods(m):
    return m.load_foods(DATA)


@pytest.fixture(scope="session")
def measures(m):
    return m.load_measures(DATA)
