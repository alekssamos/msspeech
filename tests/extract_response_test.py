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
async def test_extract_response_bytes(mss):
    expected_headers = {
        "X-RequestId": "586e68cb7617113bee75",
        "Content-Type": "audio/webm; codec=opus",
        "X-StreamId": "D9C8CDE8B3E2451D84D416C9A44310CC",
        "Path": "audio",
    }
    expected_body = b"theaudiofile"
    response = (
        b".."
        + b"X-RequestId:586e68cb7617113bee75\r\n"
        + b"Content-Type:audio/webm; codec=opus\r\n"
        + b"X-StreamId:D9C8CDE8B3E2451D84D416C9A44310CC\r\n"
        + b"Path:audio\r\n"
        + b"theaudiofile"
    )
    headers, body = mss._extract_response(response)
    assert body == expected_body
    # assert headers["X-RequestId"] == expected_headers["X-RequestId"]
    assert headers["X-StreamId"] == expected_headers["X-StreamId"]
    assert headers["Content-Type"] == expected_headers["Content-Type"]
    assert headers["Path"] == expected_headers["Path"]
