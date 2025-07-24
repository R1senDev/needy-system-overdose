from core.utils import *


def test_utilitary_class() -> None:
    class TestClass(UtilitaryClass):
        pass
    try:
        TestClass()
    except RuntimeError:
        assert True
        return
    assert False