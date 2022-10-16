import asyncio
from typing import AsyncGenerator, Generator, Tuple
from aiohttp.test_utils import TestClient, TestServer
import pytest
import pytest_asyncio
from msspeech import MSSpeech


@pytest.fixture
def mss(monkeypatch) -> Generator[MSSpeech, None, None]:
    "Creating an object from a MSSpeech class and set 2 english voices in to list"

    async def fake_get_voices_list(obj):
        obj._voices_list = [
            {
                "Name": "Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)",
                "ShortName": "en-US-GuyNeural",
                "Gender": "Male",
                "Locale": "en-US",
                "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
                "FriendlyName": "Microsoft Guy Online (Natural) - English (United States)",
                "Status": "GA",
                "VoiceTag": {
                    "ContentCategories": ["News", "Novel"],
                    "VoicePersonalities": ["Passion"],
                },
            },
            {
                "Name": "Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)",
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "Locale": "en-US",
                "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
                "FriendlyName": "Microsoft Aria Online (Natural) - English (United States)",
                "Status": "GA",
                "VoiceTag": {
                    "ContentCategories": ["News", "Novel"],
                    "VoicePersonalities": ["Positive", "Confident"],
                },
            },
        ]
        return obj._voices_list

    monkeypatch.setattr("msspeech.MSSpeech.get_voices_list", fake_get_voices_list)
    mss = MSSpeech()
    yield mss


@pytest_asyncio.fixture
async def cli_srv_mss(
    monkeypatch,
) -> AsyncGenerator[Tuple[TestClient, TestServer, MSSpeech], None]:
    "Create and return mock client and server for msspeech API and return mocked MSSpeech class instance"
    from aiohttp import web
    from unittest.mock import mock_open, patch

    @web.middleware
    async def check_request(request, handler):
        "check token"
        if request.query.get("trustedclienttoken", "") != "testtoken":
            return web.Response(body="", status=401)
        response = await handler(request)
        return response

    app = web.Application(middlewares=[check_request])
    routes = web.RouteTableDef()

    @routes.get("/consumer/speech/synthesize/readaloud/voices/list")
    async def get_voices_list_handler(request):
        "Returns a list of 3 voices"
        return web.json_response(
                [
            {
                "Name": "Microsoft Server Speech Text to Speech Voice (en-US, JennyNeural)",
                "ShortName": "en-US-JennyNeural",
                "Gender": "Female",
                "Locale": "en-US",
                "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
                "FriendlyName": "Microsoft Jenny Online (Natural) - English (United States)",
                "Status": "GA",
                "VoiceTag": {
                  "ContentCategories": [
                    "Conversation",
                    "News"
                  ],
                  "VoicePersonalities": [
                    "Friendly",
                    "Considerate",
                    "Comfort"
                  ]
                }
            },
            {
                "Name": "Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)",
                "ShortName": "en-US-GuyNeural",
                "Gender": "Male",
                "Locale": "en-US",
                "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
                "FriendlyName": "Microsoft Guy Online (Natural) - English (United States)",
                "Status": "GA",
                "VoiceTag": {
                    "ContentCategories": ["News", "Novel"],
                    "VoicePersonalities": ["Passion"],
                },
            },
            {
                "Name": "Microsoft Server Speech Text to Speech Voice (en-US, AriaNeural)",
                "ShortName": "en-US-AriaNeural",
                "Gender": "Female",
                "Locale": "en-US",
                "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
                "FriendlyName": "Microsoft Aria Online (Natural) - English (United States)",
                "Status": "GA",
                "VoiceTag": {
                    "ContentCategories": ["News", "Novel"],
                    "VoicePersonalities": ["Positive", "Confident"],
                },
            },

                ]
        )

    app.add_routes(routes)

    test_server = TestServer(app)
    await test_server.start_server()
    test_client = TestClient(test_server)
    monkeypatch.setattr("msspeech.os.path.isfile", lambda x: False)
    monkeypatch.setattr("msspeech._voices_list", [])
    monkeypatch.setattr(
        "msspeech.MSSpeech.endpoint",
        f"{test_server.scheme}://{test_server.host}:{test_server.port}/",
    )
    monkeypatch.setattr("msspeech.MSSpeech.trustedclienttoken", "testtoken")
    with patch("builtins.open", new_callable=mock_open):
        yield (test_client, test_server, MSSpeech())
    await test_client.close()
