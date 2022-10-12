import asyncio
import pytest
from msspeech import MSSpeech


@pytest.fixture
def mss():
    "Creating an object from a MSSpeech class"
    mss = MSSpeech()
    yield mss

