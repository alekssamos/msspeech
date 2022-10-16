import asyncio
import pytest


@pytest.mark.asyncio
async def test_extract_response_str(mss):
    expected_headers = {"Content-Type": "text/plain"}
    expected_body = "hello!"
    response = "Content-Type:text/plain\r\n\r\nhello!"
    headers, body = mss._extract_response(response)
    assert headers == expected_headers
    assert body == expected_body


@pytest.mark.asyncio
# @pytest.mark.xfail()
async def test_extract_response_bytes(mss, sp_audio):
    expected_headers = {
        "X-RequestId": "586e68cb7617113bee75",
        "Content-Type": "audio/webm; codec=opus",
        "X-StreamId": "D9C8CDE8B3E2451D84D416C9A44310CC",
        "Path": "audio",
    }
    expected_body = b"theaudiofile"
    response = sp_audio
    headers, body = mss._extract_response(response)
    assert body == expected_body
    assert headers == expected_headers
