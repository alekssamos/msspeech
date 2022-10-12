import asyncio
import pytest

@pytest.mark.asyncio
async def test_pitch(mss):
    await mss.set_pitch(26)
    assert 26 == (await mss.get_pitch())
