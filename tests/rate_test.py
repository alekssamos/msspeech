import asyncio
import pytest


@pytest.mark.asyncio
async def test_rate(mss):
    await mss.set_rate(15)
    assert 15 == (await mss.get_rate())
