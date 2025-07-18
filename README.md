# msspeech
not official API for Microsoft speech synthesis from Microsoft Edge web browser read aloud

## Installation

`pip install --upgrade msspeech`

or

`poetry add msspeech`


After updating an already installed library
To update the list of voices, run the command in your terminal:

`msspeech-update-voices`

or

`poetry run msspeech-update-voices`


## Notes
### Bad news

Since the first of July 2022,
the list of voices and the API as a whole has been very much limited!

### But there is also good news

They returned back some male voices and added new languages, as well as made support for emotional styles.
Despite the fact that styles appeared in JSON, you still won't be able to use them, SSML does not perceive them.
SSML is very limited here, so there is no point in supporting it.

The official documentation is not suitable for this API. It seems this API uses **undocumented** SSML markup.

https://docs.microsoft.com/ru-ru/azure/cognitive-services/speech-service/language-support#text-to-speech

## Using
the pitch and rate values are set as a percentage from -100 to +100,
that is, it can be a negative, positive number, or zero for the default value.

examples: -30, 40, 0


The volume should be a fractional number from 0.1 to 1.0, but in fact it doesn't work for some reason.


The maximum synthesize text length is approximately 9000 characters per request.

### from CLI

synthesize text:

`msspeech Guy hello --filename audio.mp3`

update voices list:

`msspeech-update-voices`

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
	await mss.set_rate(10)
	await mss.set_pitch(0)
	await mss.set_volume(1.0)
	await mss.synthesize(text.strip(), filename)
	print("*"*10)
	print("SUCCESS! OK!")
	print("*"*10)

if __name__ == "__main__":
	asyncio.run(main())
```
