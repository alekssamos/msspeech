import asyncio
import pytest


@pytest.mark.asyncio
async def test_build_request_str(mss):
    headers = {"Content-Type": "text/plain"}
    body = "hello!"
    result = mss._build_request(headers, body)
    expected_result = b"Content-Type:text/plain\r\n\r\nhello!"
    assert result == expected_result


@pytest.mark.asyncio
async def test_build_request_bytes(mss):
    headers = {"Content-Type": "audio/mpeg"}
    body = b"theaudiofile"
    result = mss._build_request(headers, body)
    expected_result = b"Content-Type:audio/mpeg\r\n\r\ntheaudiofile"
    assert result == expected_result
