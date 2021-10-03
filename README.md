# msspeech
not official API for Microsoft speech synthesis from Microsoft Edge web browser read aloud

### SUPER UPDATE!

Hidden voices!!!

https://docs.microsoft.com/ru-ru/azure/cognitive-services/speech-service/language-support#text-to-speech

## Example
```python
import asyncio
from msspeech import MSSpeech


async def main():
	mss = MSSpeech()
	print("Geting voices...")
	voices = await mss.get_voices_list()
	print("searching Russian voice...")
	for voice in voices:
		if voice["Locale"] == "ru-RU":
			print("Russian voice found:", voice["FriendlyName"])
			await mss.set_voice(voice["Name"])


	# or
	# await mss.set_voice("ru-RU-DmitryNeural")
	# await mss.set_voice("ru-RU-DariyaNeural")
	print("*" * 10)
	filename = "audio.mp3"
	# with open("s.txt", encoding="UTF8") as f: text:str = f.read()
	text = "Или написать текст здесь"
	print("waiting...")
	await mss.set_rate(1)
	await mss.set_pitch(0)
	await mss.set_volume(2)
	await mss.synthesize(text.strip(), filename)
	print("*"*10)
	print("SUCCESS! OK!")
	print("*"*10)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
```

The maximum text length is approximately 31,000 characters.
