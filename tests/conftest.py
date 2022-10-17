import asyncio
from typing import AsyncGenerator, Generator, Tuple
from aiohttp.test_utils import TestClient, TestServer
import aiohttp
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


@pytest.fixture
def sp_audio()->bytes:
    return (
        b".."
        + b"X-RequestId:586e68cb7617113bee75\r\n"
        + b"Content-Type:audio/webm; codec=opus\r\n"
        + b"X-StreamId:D9C8CDE8B3E2451D84D416C9A44310CC\r\n"
        + b"Path:audio\r\n"
        + b"theaudiofile"
    )

@pytest.fixture
def sp_config()->dict:
    return {
        "context": {
            "synthesis": {
                "audio": {
                    "metadataoptions": {
                        "sentenceBoundaryEnabled": "false",
                        "wordBoundaryEnabled": "true",
                    },
                    "outputFormat": "audio-24khz-48kbitrate-mono-mp3",
                }
            }
        }
    }



@pytest_asyncio.fixture
async def cli_srv_mss(
    monkeypatch,
    sp_audio,
    sp_config,
    aiohttp_client,
    aiohttp_server,
    tmp_path,
) -> AsyncGenerator[Tuple[TestClient, TestServer, MSSpeech], None]:
    "Create and return mock client and server for msspeech API and return mocked MSSpeech class instance"
    from aiohttp import web
    import json

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

    @routes.get("/consumer/speech/synthesize/readaloud/edge/v1")
    async def websocket_handler(request):

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    headers, body = msg.data.split("\r\n\r\n", 1)
                    if "Content-Type:application/json" in headers and "Path:speech.config" in headers:
                        body = json.loads(body)
                        assert body == sp_config
                        await ws.send_str("""Content-Type:application/json\r\nPath:qwe.rty\r\n\r\n{"something":"not_used_for_me"}""")
                    if "Content-Type:application/ssml+xml" in headers and "Path:ssml" in headers:
                        for x in [
                            "<speak", "<voice", "</prosody>",
                            "</speak>", "</voice>", "</prosody>",
                        ]:
                            assert x in body
                        await ws.send_bytes(sp_audio)
                        await ws.send_str("""Content-Type:application/json\r\nPath:qwe.rty\r\n\r\n{"something":"not_used_for_me"}""")
                        await ws.send_str("""Content-Type:application/json\r\nPath:qwe.rty\r\n\r\n{}""")
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' %
                      ws.exception())

        print('websocket connection closed')

        return ws

    app.add_routes(routes)

    test_server = await aiohttp_server(app)
    await test_server.start_server()
    test_client = await aiohttp_client(test_server)
    monkeypatch.setattr("msspeech.os.path.isfile", lambda x: False)
    monkeypatch.setattr("msspeech._voices_list", [])
    monkeypatch.setattr(
        "msspeech.MSSpeech.endpoint",
        f"{test_server.scheme}://{test_server.host}:{test_server.port}/",
    )
    monkeypatch.setattr("msspeech.MSSpeech.trustedclienttoken", "testtoken")
    monkeypatch.setattr("msspeech.msspeech_dir", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    yield (test_client, test_server, MSSpeech())
    await test_client.close()
