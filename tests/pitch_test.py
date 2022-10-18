import asyncio
import pytest


@pytest.mark.asyncio
async def test_pitch(mss):
    await mss.set_pitch(26)
    assert 26 == (await mss.get_pitch())


@pytest.mark.parametrize("p", [-555, 444])
@pytest.mark.asyncio
async def test_incorrect_pitch(mss, p):
    with pytest.raises(ValueError):
        await mss.set_pitch(p)


