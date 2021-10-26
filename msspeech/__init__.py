"""not official API for Microsoft speech synthesis from Microsoft Edge web browser read aloud"""

import re
import asyncio
import aiofiles
import os, os.path
import html
from typing import Any, List, Dict, Tuple, Union
from urllib.parse import urlencode
import aiohttp
import json

bytes_or_str = Union[str, bytes]

msspeech_dir = os.path.dirname(__file__)
class MSSpeechError(Exception):
	pass

_voices_list:List = []

class MSSpeech():
	"""Microsoft speech online unofficial API
	"""
	endpoint:str = "https://speech.platform.bing.com/"
	trustedclienttoken:str = "6A5AA1D4EAFF4E9FB37E23D68491D6F4"
	headers:dict = {
		"Pragma": "no-cache",
		"Cache-Control": "no-cache",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52",
		"Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold"
	}

	errors = {
		1007: "One or more parameters in SSML are not valid"
	}
	for k, v in errors.items():
		errors[k] = v + " #" + str(k)

	synthesis_config: dict = {
		"context": {
			"synthesis": {
				"audio": {
					"metadataoptions": {
						"sentenceBoundaryEnabled": "false",
						"wordBoundaryEnabled": "true"
					},
					"outputFormat": "audio-24khz-48kbitrate-mono-mp3"
				}
			}
		}
	}

	voiceName:str = ""
	# voiceName = "Microsoft Server Speech Text to Speech Voice (ru-RU, SvetlanaNeural)"
	pitch:int = 0
	volume:int = 0
	rate:int = 0
	def __init__(self):
		"""Create class instance
		"""

	@staticmethod
	def _int_to_str(i:int)->str:
		return "+"+str(i) if i >= 0 else str(i)

	async def set_pitch(self, pitch:int)->None:
		self.pitch = int(pitch)

	async def set_volume(self, volume:int)->None:
		self.volume = int(volume)

	async def set_rate(self, rate:int)->None:
		self.rate = int(rate)

	async def get_pitch(self)->int:
		return self.pitch

	async def get_volume(self)->int:
		return self.volume

	async def get_rate(self)->int:
		return self.rate

	async def set_voice(self, voiceName:str)->None:
		if not isinstance(voiceName, str):
			raise TypeError("Not the correct data type. Required str. You passed "+type(voiceName).__name__)
		voiceName = voiceName.strip()
		if len(voiceName) < 1:
			raise ValueError("voiceName is empty")
		voices:List[Dict] = await self.get_voices_list()
		voiceNames:List = [v["Name"] for v in voices if "FriendlyName" in v]
		voiceShortNames:List = [v["ShortName"] for v in voices if "FriendlyName" in v]
		if not voiceName in voiceNames+voiceShortNames:
			raise ValueError("Unknown voice "+voiceName)
		self.voiceName = voiceName

	async def get_voice(self)->dict:
		voices:List[Dict] = await self.get_voices_list()
		for voice in voices:
			if voice["Name"].strip() == self.voiceName.strip() or voice["ShortName"].strip() == self.voiceName.strip():
				return voice
		return {}

	@staticmethod
	def _build_request(headers:Dict[str, str], body:bytes_or_str) -> bytes:
		s:str = "\r\n".join([str(k)+":"+str(v) for k, v in headers.items()]) + "\r\n\r\n"
		b:Any = body.encode("UTF8") if isinstance(body, str) else bytes(body)
		return bytes(s.encode("UTF8") + b)

	@staticmethod
	def _extract_response(response:bytes_or_str) -> Tuple[dict, bytes_or_str]:
		offset:int = 130
		headers:Any = {}
		body:bytes_or_str = ""
		if isinstance(response, bytes):
			headers, body = (response[2:(offset-1)], response[offset:])
		elif isinstance(response, str):
			headers, body = response.split("\r\n\r\n", 1)
		else:
			raise TypeError("Not the correct data type. str or bytes required. You passed "+type(response).__name__)
		if isinstance(headers, bytes):
			headers = headers.decode("utf8")
		headers = headers.strip()
		parsed_headers:Dict[str, str] = dict([line.split(":", 1) for line in headers.split("\r\n")])
		return (parsed_headers, body)

	async def get_voices_list(self) -> List[Dict]:
		"""Returns all available voices

		Returns:
			List[Dict]: languages and voices
			Example:
			```javascript
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
			```
		"""

		global _voices_list
		if len(_voices_list) > 0:
			return _voices_list
		voicesplusfilepath = os.path.join(msspeech_dir, "voices_list_plus.json")
		if os.path.isfile(voicesplusfilepath):
			with open(voicesplusfilepath, encoding="UTF8") as f: _voices_list = json.load(f)
		if len(_voices_list) > 0:
			return _voices_list
		async with aiohttp.ClientSession(headers = self.headers) as session:
			async with session.get(self.endpoint + "consumer/speech/synthesize/readaloud/voices/list",
					params={"trustedclienttoken":self.trustedclienttoken}) as resp:
				_voices_list = await resp.json()
				return _voices_list

	async def synthesize(self, text:str, filename_or_buffer:Any)-> int:
		"returns the number of bytes written in an MP3 file"
		rplimit = 50
		for rpcount in range(1, rplimit+1):
			try:
				res = await self._synthesize(text, filename_or_buffer)
				return res
			except (aiohttp.ClientError, ValueError) as e:
				if rpcount==rplimit:
					raise
				await asyncio.sleep(10)

	async def _synthesize(self, text:str, filename_or_buffer:Any)-> int:
		bc:int=0
		if len(text.strip()) < 1:
			raise ValueError("the text cannot be empty")
		async with aiohttp.ClientSession(headers = self.headers) as session:
			ws = await session.ws_connect(self.endpoint + "consumer/speech/synthesize/readaloud/edge/v1?" + urlencode({
				"trustedclienttoken":self.trustedclienttoken
			}))
			await ws.send_str(
				self._build_request({
				"Content-Type":"application/json; charset=utf-8",
				"Path":"speech.config"
				},
				json.dumps(self.synthesis_config)).decode("UTF8")
			)
			text = html.escape(text)
			text = text.replace("\r\n", "\n").replace("\r", "\n")
			text = re.sub(r"([^\n])[\n]([^\n])", r"\1 \2", text)
			text = re.sub(r"([^.])[\s]\.([^.])", r"\1. \2", text)
			text = re.sub(r"[ \t]{2,}", r" ", text)
			CHARACTER_TO_ESCAPE = {
				'<' : '&lt;',
				'>' : '&gt;',
				'&' : '&amp;',
				'"' : '&quot;',
				'\'' : '&apos;',
			}
			ESCAPE_TO_CHARACTER = {
				'&lt;' : '<',
				'&gt;' : '>' ,
				'&amp;' : '&',
				'&quot;' : '"',
				'&apos;' : '\'',
			}
			STANDARD_CONVERSION = {
				'‘' : '\'',
				'’' : '\'',
				'‛' : '\'',
				'‚' : '\'',
				'′' : '\'',
				'“' : '"',
				'”' : '"',
				'„' : '"',
				'‟' : '"',
				'″' : '"',
			}

			for k, v in STANDARD_CONVERSION.items(): text = text.replace(k, v)
			for k, v in CHARACTER_TO_ESCAPE.items(): text = text.replace(k, v)
			if (await self.get_voice())["Locale"][0:2].lower() == "ua":
				text = text.replace("ў","у")
				text = text.replace("Ў","У")
			if (await self.get_voice())["Locale"][0:2].lower() == "ru":
				text = text.replace("і","и")
				text = text.replace("І","И")
				text = text.replace("і","и")
				text = text.replace("ў","у")
				text = text.replace("Ў","У")
				text = text.replace("'","ъ")
			for c in range(0, 32):
				if c not in [9, 10, 13]:
					text = text.replace(chr(c), " ")
			await ws.send_str(
				self._build_request({
				"X-RequestId":"586bb1cb2bbe2e68bb1e7617113bee75",
				"Content-Type":"application/ssml+xml",
				"Path":"ssml"
				},
				"""
<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'><voice  name='{voiceName}'><prosody pitch='{pitch}Hz' rate ='{rate}%' volume='{volume}%'> {text}</prosody></voice></speak>
			""".strip().format(
				text = text,
				voiceName = self.voiceName,
				pitch = self._int_to_str(self.pitch),
				rate = self._int_to_str(self.rate),
				volume = self._int_to_str(self.volume)
			)).decode("UTF8")
			)
			f:Any = None
			while True:
				msg = await ws.receive()
				if (f is not None and msg.type == aiohttp.WSMsgType.text and 'json' in msg.data and len(json.loads(self._extract_response(msg.data)[1])) == 0) or (msg.type == aiohttp.WSMsgType.closed or msg.type == aiohttp.WSMsgType.error):
					await ws.close()
					break
				if isinstance(msg.data, int):
					await ws.close()
					raise MSSpeechError(self.errors.get(msg.data, "unknown error #"+str(msg.data)))
					break
				resp = self._extract_response(msg.data)
				if isinstance(resp[1], bytes):
					if f is None:
						if isinstance(filename_or_buffer, str):
							f = await aiofiles.open(filename_or_buffer, "wb")
						else:
							f = filename_or_buffer
					bc += (await f.write(resp[1]))
			if f is not None and isinstance(filename_or_buffer, str):
				await f.close()
			f = None
			return bc
