import asyncio
from typing import Tuple
from aiohttp.test_utils import TestClient, TestServer
import pytest
from msspeech import MSSpeech


@pytest.fixture
def mss(monkeypatch):
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


@pytest.fixture
def cli_srv() -> Tuple[TestClient, TestServer]:
    "Create and return mock client and server form msspeech API"
    from aiohttp import web
    import json

    @web.middleware
    async def check_request(request, handler):
        "check token"
        if (
            request.query.get("trustedclienttoken", "")
            != "6A5AA1D4EAFF4E9FB37E23D68491D6F4"
        ):
            return web.Response(body="", status=401)
        response = await handler(request)
        return response

    app = web.Application(middlewares=[check_request])
    routes = web.RouteTableDef()

    @routes.get("/consumer/speech/synthesize/readaloud/voices/list")
    async def get_voices_list_handler(request):
        return web.json_response(
            json.loads(
                """[
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
              {
                "Name": "Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)",
                "ShortName": "en-US-GuyNeural",
                "Gender": "Male",
                "Locale": "en-US",
                "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
                "FriendlyName": "Microsoft Guy Online (Natural) - English (United States)",
                "Status": "GA",
                "VoiceTag": {
                  "ContentCategories": [
                    "News",
                    "Novel"
                  ],
                  "VoicePersonalities": [
                    "Passion"
                  ]
                }
              },
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
                "Name": "Microsoft Server Speech Text to Speech Voice (en-US, MichelleNeural)",
                "ShortName": "en-US-MichelleNeural",
                "Gender": "Female",
                "Locale": "en-US",
                "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
                "FriendlyName": "Microsoft Michelle Online (Natural) - English (United States)",
                "Status": "GA",
                "VoiceTag": {
                  "ContentCategories": [
                    "News",
                    "Novel"
                  ],
                  "VoicePersonalities": [
                    "Friendly",
                    "Pleasant"
                  ]
                }
              },
              {
                "Name": "Microsoft Server Speech Text to Speech Voice (en-US, RogerNeural)",
                "ShortName": "en-US-RogerNeural",
                "Gender": "Male",
                "Locale": "en-US",
                "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
                "FriendlyName": "Microsoft Roger Online (Natural) - English (United States)",
                "Status": "GA",
                "VoiceTag": {
                  "ContentCategories": [
                    "News",
                    "Novel"
                  ],
                  "VoicePersonalities": [
                    "Lively"
                  ]
                }
              },
              {
                "Name": "Microsoft Server Speech Text to Speech Voice (en-ZA, LeahNeural)",
                "ShortName": "en-ZA-LeahNeural",
                "Gender": "Female",
                "Locale": "en-ZA",
                "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
                "FriendlyName": "Microsoft Leah Online (Natural) - English (South Africa)",
                "Status": "GA",
                "VoiceTag": {
                  "ContentCategories": [
                    "General"
                  ],
                  "VoicePersonalities": [
                    "Friendly",
                    "Positive"
                  ]
                }
              },
              {
                "Name": "Microsoft Server Speech Text to Speech Voice (en-ZA, LukeNeural)",
                "ShortName": "en-ZA-LukeNeural",
                "Gender": "Male",
                "Locale": "en-ZA",
                "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
                "FriendlyName": "Microsoft Luke Online (Natural) - English (South Africa)",
                "Status": "GA",
                "VoiceTag": {
                  "ContentCategories": [
                    "General"
                  ],
                  "VoicePersonalities": [
                    "Friendly",
                    "Positive"
                  ]
                }
              }
        ]"""
            )
        )

    test_server = TestServer(app)
    test_client = TestClient(test_server)
    return (test_client, test_server)
