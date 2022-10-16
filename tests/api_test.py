import asyncio
import pytest


@pytest.mark.asyncio
async def test_get_voices_list_api(cli_srv_mss):
    client, server, mss = cli_srv_mss
    voices = await mss.get_voices_list()
    assert len(voices) == 3  # check API mock
