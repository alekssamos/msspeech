import asyncio
import pytest


@pytest.mark.asyncio
async def test_parse_multivoices_wwith_default_params(mss):
    voices = await mss.get_voices_list()
    assert len(voices) == 2 # check mock
    input_text = "%Guy: Hi, Aria!\n%Aria: Hello, Guy!".strip()
    expected_ssml = "<voice  name='en-US-GuyNeural'><prosody pitch='0Hz' rate ='+0%' volume='+1.0'> Hi, Aria!</prosody></voice>\n\n<voice  name='en-US-AriaNeural'><prosody pitch='0Hz' rate ='+0%' volume='+1.0'> Hello, Guy!</prosody></voice>".strip()
    result = (await mss.parse_multivoices(input_text)).strip()
    assert expected_ssml == result
