import asyncio
import pytest


@pytest.mark.asyncio
async def test_rate(mss):
    await mss.set_rate(15)
    assert 15 == (await mss.get_rate())


@pytest.mark.parametrize("r", [-777, 888])
@pytest.mark.asyncio
async def test_incorrect_rate(mss, r):
    with pytest.raises(ValueError):
        await mss.set_rate(r)


