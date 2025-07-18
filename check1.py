#!/usr/bin/env python3
import time
import asyncio
from msspeech import MSSpeech


async def main():
    mss = MSSpeech()
    # 	print("Geting voices...")
    # 	voices = await mss.get_voices_list()
    # 	print("searching Russian voice...")
    # 	for voice in voices:
    # 		if voice["Locale"] == "ru-RU":
    # 			print("Russian voice found:", voice["FriendlyName"])
    # 			await mss.set_voice(voice["Name"])

    await mss.set_voice("ru-RU-DmitryNeural")
    print("*" * 10)
    filename = "m_full.mp3"
    with open(r"E:\massage.txt", encoding="UTF8") as f:
        text: str = f.read()
    print("waiting...")
    await mss.set_rate(100)
    await mss.set_pitch(0)
    await mss.set_volume(1.0)
    starttime=time.time()
    await mss.synthesize(text.strip(), filename)
    endtime=time.time()
    difftime=endtime-starttime
    print("*" * 10)
    print("SUCCESS! OK! Execution time: ", difftime)
    print("*" * 10)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
