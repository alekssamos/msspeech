#!/usr/bin/env python3
import asyncio
from msspeech import MSSpeech


async def main():
	mss = MSSpeech()
#	print("Geting voices...")
#	voices = await mss.get_voices_list()
#	print("searching Russian voice...")
#	for voice in voices:
#		if voice["Locale"] == "ru-RU":
#			print("Russian voice found:", voice["FriendlyName"])
#			await mss.set_voice(voice["Name"])


#	await mss.set_voice("ru-RU-DmitryNeural")
	await mss.set_voice("ru-RU-DariyaNeural")
	print("*" * 10)
	filename = "full.mp3"
	with open("s.txt", encoding="UTF8") as f: text:str = f.read()
	text = "Дарья! Здесь тоже есть Даша! Дашуля! Вот это да! Сейчас я распарсю эту таблицу в Джейсон и запихаю в эту функцию! Какой улыбчивый, но довольно спокойный голос."
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
