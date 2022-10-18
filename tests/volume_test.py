import asyncio
import pytest


@pytest.mark.asyncio
async def test_volume(mss):
    await mss.set_volume(1.0)
    assert 1.0 == (await mss.get_volume())


@pytest.mark.parametrize("v", [-777.3, 888.9])
@pytest.mark.asyncio
async def test_incorrect_volume(mss, v):
    with pytest.raises(ValueError):
        await mss.set_volume(v)


def test_normalize_volume(mss):
    assert mss._normalize_volume(0.5) == 50
