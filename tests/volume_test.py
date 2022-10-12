import asyncio
import pytest

@pytest.mark.asyncio
async def test_volume(mss):
    await mss.set_volume(1.0)
    assert 1.0 == (await mss.get_volume())

@pytest.mark.asyncio
async def test_incorrect_volume(mss):
    with pytest.raises(ValueError):
        await mss.set_volume(-3.2)
    with pytest.raises(ValueError):
        await mss.set_volume(2.3)
