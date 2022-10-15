from msspeech import ireplace
import pytest

def test_ireplace(mss):
    assert ireplace("w", "x", "qWe") == "qxe"
    assert ireplace("S", "Y", "AsD") == "AYD"
    assert ireplace("", "", "") == ""
