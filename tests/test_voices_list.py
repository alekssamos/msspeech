import asyncio
import pytest
from aiohttp import web
from msspeech import MSSpeech

@pytest.fixture
def event_loop():
	loop = asyncio.get_event_loop()
	yield loop
	loop.close()

async def voices_list_ok(request):
	if "trustedclienttoken" not in request.rel_url.query or len(request.rel_url.query.get("trustedclienttoken", "")) < 10:
		raise web.HTTPNotFound()
	data = json.loads("""
[
  {
    "Name": "Microsoft Server Speech Text to Speech Voice (ar-EG, SalmaNeural)",
    "ShortName": "ar-EG-SalmaNeural",
    "Gender": "Female",
    "Locale": "ar-EG",
    "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
    "FriendlyName": "Microsoft Salma Online (Natural) - Arabic (Egypt)",
    "Status": "GA"
  },
  {
    "Name": "Microsoft Server Speech Text to Speech Voice (ar-SA, ZariyahNeural)",
    "ShortName": "ar-SA-ZariyahNeural",
    "Gender": "Female",
    "Locale": "ar-SA",
    "SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
    "FriendlyName": "Microsoft Zariyah Online (Natural) - Arabic (Saudi Arabia)",
    "Status": "GA"
  }
]
""".strip())
	return web.json_response(data)

def create_app(get_event_loop):
	app = web.Application(loop=get_event_loop)
	app.router.add_route('GET', '/consumer/speech/synthesize/readaloud/voices/list', voices_list_ok)
	return app

async def test_voices_list(test_client):
	client = await test_client(create_app)
	msp = MSSpeech()
	resp = await msp.voices_list()

	assert len(resp) > 0
	assert "Name" in resp[-1]
	assert "ShortName" in resp[-1]
	assert "Gender" in resp[-1]
	assert "Locale" in resp[-1]
	assert "FriendlyName" in resp[-1]
