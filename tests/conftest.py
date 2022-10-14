import asyncio
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
