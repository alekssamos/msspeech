#!/usr/bin/env python3
import asyncio
import sys
import os.path
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
	filename = "full.mp3"
	text:str = sys.argv[-1]
	if len(sys.argv[-1]) < 255 and os.path.isfile(sys.argv[-1]):
		with open(sys.argv[-1], "r", encoding="UTF8") as f:
			text = f.read()
	# print(text)
	print("waiting...")
	await mss.set_rate(80)
	await mss.set_pitch(-20)
	await mss.set_volume(2)
	await mss.synthesize(text.strip(), filename)
	print("*"*10)
	print("SUCCESS! OK!")
	print("*"*10)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
