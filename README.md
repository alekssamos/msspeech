# msspeech
not official API for Microsoft speech synthesis from Microsoft Edge web browser read aloud

## Installation

`poetry add msspeech && poetry install`

or

`pip install --upgrade msspeech`

or

`pip install  --upgrade https://github.com/alekssamos/msspeech/archive/refs/heads/main.zip`

After updating an already installed library
To update the list of voices, run the command in your terminal:
`msspeech_update_voices`

or

`poetry run msspeech_update_voices`


## Notes
### Bad news

Since the first of July 2022,
the list of voices and the API as a whole has been very much limited!

### But there is also good news

They returned back some male voices and added new languages, as well as made support for emotional styles.
Despite the fact that styles appeared in JSON, you still won't be able to use them, SSML does not perceive them.
SSML is very limited here, so there is no point in supporting it.

https://docs.microsoft.com/ru-ru/azure/cognitive-services/speech-service/language-support#text-to-speech

## Using
### from CLI

synthesize text:

`msspeech Guy hello --filename audio.mp3`

update voices:

`msspeech_update_voices`

### From python
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


	print("*" * 10)
	filename = "audio.mp3"
	# with open("s.txt", encoding="UTF8") as f: text:str = f.read()
	text = "Или написать текст здесь"
	print("waiting...")
	await mss.set_rate(1)
	await mss.set_pitch(0)
	await mss.set_volume(1)
	await mss.synthesize(text.strip(), filename)
	print("*"*10)
	print("SUCCESS! OK!")
	print("*"*10)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
```

The maximum text length is approximately 31,000 characters.
