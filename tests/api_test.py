import asyncio
import pytest
from msspeech import MSSpeechError

@pytest.mark.asyncio
async def test_get_voices_list_api(cli_srv_mss):
    client, server, mss = cli_srv_mss
    voices = await mss.get_voices_list()
    assert len(voices) == 3  # check API mock

@pytest.mark.asyncio
async def test_synthesize_api(cli_srv_mss):
    client, server, mss = cli_srv_mss
    vn = (await mss.get_voices_by_substring("Guy"))[0]["Name"]
    await mss.set_voice(vn)
    filename = "test.opus"
    await mss.synthesize("hi!", filename)
    with open(filename, "rb") as f:
        assert f.read() == b"theaudiofile"

@pytest.mark.asyncio
async def test_error_synthesize_api(cli_srv_mss):
    client, server, mss = cli_srv_mss
    vn = (await mss.get_voices_by_substring("Guy"))[0]["Name"]
    await mss.set_voice(vn)
    filename = "test.opus"
    try:
        await mss.synthesize("ssml error", filename)
        assert False
    except MSSpeechError as e_info:
        assert e_info.code == 1007

    assert True
