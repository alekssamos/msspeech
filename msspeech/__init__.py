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
import ssl

bytes_or_str = Union[str, bytes]

msspeech_dir = os.path.dirname(__file__)

def ireplace(old, repl, text):
    return re.sub('(?i)'+re.escape(old), lambda m: repl, text)

class MSSpeechError(Exception):
    pass


_voices_list: List = []


class MSSpeech:
    """Microsoft speech online unofficial API"""

    endpoint: str = "https://speech.platform.bing.com/"
    trustedclienttoken: str = "6A5AA1D4EAFF4E9FB37E23D68491D6F4"
    headers: dict = {
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52",
        "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
    }

    errors = {1007: "One or more parameters in SSML are not valid"}
    for k, v in errors.items():
        errors[k] = v + " #" + str(k)

    synthesis_config: dict = {
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

    voiceName: str = ""
    # voiceName = "Microsoft Server Speech Text to Speech Voice (ru-RU, SvetlanaNeural)"
    pitch: int = 0
    volume: int = 0
    rate: int = 0
    config_sended: bool = False

    def __init__(self):
        """Create class instance"""

    @staticmethod
    def _int_to_str(i: int) -> str:
        return "+" + str(i) if i >= 0 else str(i)

    async def set_pitch(self, pitch: int) -> None:
        self.pitch = int(pitch)

    async def set_volume(self, volume: int) -> None:
        self.volume = int(volume)

    async def set_rate(self, rate: int) -> None:
        self.rate = int(rate)

    async def get_pitch(self) -> int:
        return self.pitch

    async def get_volume(self) -> int:
        return self.volume

    async def get_rate(self) -> int:
        return self.rate

    async def set_voice(self, voiceName: str) -> None:
        if not isinstance(voiceName, str):
            raise TypeError(
                "Not the correct data type. Required str. You passed "
                + type(voiceName).__name__
            )
        voiceName = voiceName.strip()
        if len(voiceName) < 1:
            raise ValueError("voiceName is empty")
        voices: List[Dict] = await self.get_voices_list()
        voiceNames: List = [v["Name"] for v in voices if "DisplayName" in v]
        voiceShortNames: List = [v["ShortName"] for v in voices if "ShortName" in v]
        voiceLocalNames: List = [v["LocalName"] for v in voices if "LocalName" in v]
        if not voiceName in voiceNames + voiceShortNames + voiceLocalNames:
            raise ValueError("Unknown voice " + voiceName)
        self.voiceName = (await self.get_voices_by_substring(voiceName))[0]['Name']

    async def get_voices_by_substring(self, substring: str) -> dict:
        """
        get   voices by substring
        """
        voices: List[Dict] = await self.get_voices_list()
        l:list = []
        for voice in voices:
            if (
                substring.strip() in voice["Name"].strip()
                or substring.strip() in voice["ShortName"].strip()
                or substring.strip() in voice["DisplayName"].strip()
                or substring.strip() in voice["LocalName"].strip()
            ):
                l.append(voice)
        return l

    async def get_voice(self) -> dict:
        voices: List[Dict] = await self.get_voices_list()
        for voice in voices:
            if (
                voice["Name"].strip() == self.voiceName.strip()
                or voice["ShortName"].strip() == self.voiceName.strip()
                or voice["DisplayName"].strip() == self.voiceName.strip()
                or voice["LocalName"].strip() == self.voiceName.strip()
            ):
                return voice
        return {}

    async def parse_multivoices(
        self,
        message,
        call_from_synthesize_function = False,
        open_voice_tag_if_needed = '',
        close_voice_tag_if_needed = '',
        default_pitch = 0,
        default_rate = 0,
        default_volume = 0
    ):
        """
        replacing voices with tags in the text
        """
        message = re.sub(r'([%][\w]+[:])', '\n' + r'\1', message, flags=re.I)
        pattern = re.compile(r'[%]([\w]+)[:](.*)', re.I)
        sudonames = {
            "DariyaNeural": ["Даша", "Дарья"],
            "SvetlanaNeural": ["Света", "Светлана"],
            "DmitryNeural": ["Дима", "Дмитрий"],
        }
        for k, v in sudonames.items():
            for sudoname in v:
                message = ireplace(f"%{sudoname}:", f"%{k}:", message)
        voices:list = await self.get_voices_list()
        replaced:str = ''
        for match in re.findall(pattern, message):
            voice_name_from_tag, text_from_tag = match
            for voice in voices:
                voiceShortName = voice['ShortName'].split("-")[-1].lower()
                if (
                    voice_name_from_tag.lower() == voiceShortName
                    or voice_name_from_tag.lower()  + "neural" == voiceShortName
                    or voice_name_from_tag.lower() == voice['DisplayName'].lower()
                    or voice_name_from_tag.lower() == voice['LocalName'].lower()
                ):
                    replaced = close_voice_tag_if_needed + """
<voice  name='{voiceName}'><prosody pitch='{pitch}Hz' rate ='{rate}%' volume='{volume}%'>{text_from_tag}</prosody></voice>
                    """.format(
                        voiceName = voice['ShortName'],
                        text_from_tag = text_from_tag,
                        pitch = default_pitch,
                        rate = self._int_to_str(default_rate),
                        volume=self._int_to_str(default_volume),
                    ).strip() + open_voice_tag_if_needed
                    message = re.sub(
                        r"[%]{}[:].*".format(voice_name_from_tag),
                        replaced.replace('\\\\', '\\'),
                        message,
                        count = 1,
                        flags = re.I
                    )
                else:
                    continue
        return message

    @staticmethod
    def _build_request(headers: Dict[str, str], body: bytes_or_str) -> bytes:
        s: str = (
            "\r\n".join([str(k) + ":" + str(v) for k, v in headers.items()])
            + "\r\n\r\n"
        )
        b: Any = body.encode("UTF8") if isinstance(body, str) else bytes(body)
        return bytes(s.encode("UTF8") + b)

    @staticmethod
    def _extract_response(response: bytes_or_str) -> Tuple[dict, bytes_or_str]:
        offset: int = 130
        headers: Any = {}
        body: bytes_or_str = ""
        if isinstance(response, bytes):
            headers, body = (response[2 : (offset - 1)], response[offset:])
        elif isinstance(response, str):
            headers, body = response.split("\r\n\r\n", 1)
        else:
            raise TypeError(
                "Not the correct data type. str or bytes required. You passed "
                + type(response).__name__
            )
        if isinstance(headers, bytes):
            headers = headers.decode("utf8")
        headers = headers.strip()
        parsed_headers: Dict[str, str] = dict(
            [line.split(":", 1) for line in headers.split("\r\n")]
        )
        return (parsed_headers, body)

    async def get_voices_list(self) -> List[Dict]:
        """Returns all available voices

        Returns:
                List[Dict]: languages and voices
                Example:
                ```javascript
                [
                  {
                    "Name": "Microsoft Server Speech Text to Speech Voice (en-US, JennyNeural)",
                    "DisplayName": "Jenny",
                    "LocalName": "Jenny",
                    "ShortName": "en-US-JennyNeural",
                    "Gender": "Female",
                    "Locale": "en-US",
                    "LocaleName": "English (United States)",
                    "StyleList": [
                      "assistant",
                      "chat",
                      "customerservice",
                      "newscast"
                    ],
                    "SampleRateHertz": "24000",
                    "VoiceType": "Neural",
                    "Status": "GA"
                  },
                  {
                    "Name": "Microsoft Server Speech Text to Speech Voice (en-US, GuyNeural)",
                    "DisplayName": "Guy",
                    "LocalName": "Guy",
                    "ShortName": "en-US-GuyNeural",
                    "Gender": "Male",
                    "Locale": "en-US",
                    "LocaleName": "English (United States)",
                    "StyleList": [
                      "newscast"
                    ],
                    "SampleRateHertz": "24000",
                    "VoiceType": "Neural",
                    "Status": "GA"
                  },
                ]
                ```
        """

        import sys
        global _voices_list
        _res = {}
        if len(_voices_list) > 0:
            return _voices_list
        voicesplusfilepath = os.path.join(msspeech_dir, "voices_list_plus.json")
        if os.path.isfile(voicesplusfilepath):
            try:
                with open(voicesplusfilepath, encoding="UTF8") as f:
                    _res= json.load(f)
                _voices_list = _res
            except json.decoder.JSONDecodeError:
                _voices_list = {}
                sys.stderr.write(f"MSSpeech.get_voices_list: error reading {voicesplusfilepath}")
        if len(_voices_list) > 0:
            return _voices_list
        async with aiohttp.ClientSession(headers=self.headers) as session:
            sys.stdout.write("MSSpeech.get_voices_list: downloading voice list JSON file...")
            async with session.get(
                # self.endpoint + "consumer/speech/synthesize/readaloud/voices/list",
                # "https://eastus.tts.speech.microsoft.com/cognitiveservices/voices/list",
                "https://raw.githubusercontent.com/alekssamos/msspeech/da5904e14e7e8b383f4230c57585eaa92271a4bb/msspeech/voices_list_plus.json",
                headers={
                    # "Referer": "https://azure.microsoft.com/",
                    # "Origin": "https://azure.microsoft.com"
                }
                # params={"trustedclienttoken": self.trustedclienttoken},
            ) as resp:
                # _voices_list = await resp.json()
                _voices_list = await resp.json(content_type = "text/plain; charset=utf-8")
                try:
                    with open(voicesplusfilepath, "w", encoding="UTF8") as fp:
                        json.dump(_voices_list, fp, ensure_ascii=False, indent=2)
                except OSError:
                    sys.stderr.write(f"MSSpeech.get_voices_list: error ssaving {voicesplusfilepath}")
                return _voices_list

    async def synthesize(self, text: str, filename_or_buffer: Any, multivoices:bool = True) -> int:
        "returns the number of bytes written in an MP3 file"
        rplimit = 50
        for rpcount in range(1, rplimit + 1):
            try:
                res = await self._synthesize(text, filename_or_buffer)
                return res
            except (aiohttp.ClientError, ssl.SSLError, ValueError) as e:
                import sys
                sys.stderr.write(
                    f"MSSpeech.synthesize: {sys.exc_info()[1]}, repeat #{rpcount}"
                )
                if rpcount == rplimit:
                    raise
                await asyncio.sleep(10)

    async def _synthesize(self, text: str, filename_or_buffer: Any, multivoices:bool = True) -> int:
        bc: int = 0
        if len(text.strip()) < 1:
            raise ValueError("the text cannot be empty")
        async with aiohttp.ClientSession(headers=self.headers) as session:
            ws = await session.ws_connect(
                self.endpoint
                + "consumer/speech/synthesize/readaloud/edge/v1?"
                + urlencode({"trustedclienttoken": self.trustedclienttoken})
            )
            await ws.send_str(
                self._build_request(
                    {
                        "Content-Type": "application/json; charset=utf-8",
                        "Path": "speech.config",
                    },
                    json.dumps(self.synthesis_config)
                ).decode("UTF8")
            )
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            text = re.sub(r"([\w])[-][\r\n]([\w])", r"\1\2", text)
            text = re.sub(r"([^\n])[\n]([^\n])", r"\1 \2", text)
            text = re.sub(r"[ \t]{2,}", r" ", text)
            text = re.sub(r"([\w])([.!?,])([\w])", r"\1\2 \3", text)
            CHARACTER_TO_ESCAPE = {
                "<": "&lt;",
                ">": "&gt;",
                "&": "&amp;",
                '"': "&quot;",
                "'": "&apos;",
            }
            ESCAPE_TO_CHARACTER = {
                "&lt;": "<",
                "&gt;": ">",
                "&amp;": "&",
                "&quot;": '"',
                "&apos;": "'",
            }
            STANDARD_CONVERSION = {
                "‘": "'",
                "’": "'",
                "‛": "'",
                "‚": "'",
                "′": "'",
                "“": '"',
                "”": '"',
                "„": '"',
                "‟": '"',
                "″": '"',
            }

            for k, v in STANDARD_CONVERSION.items():
                text = text.replace(k, v)
            for k, v in CHARACTER_TO_ESCAPE.items():
                text = text.replace(k, v)
            for c in range(0, 32):
                if c not in [9, 10, 13]:
                    text = text.replace(chr(c), " ")
            speak_element_open = "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
            speak_element_close = "</speak>"
            voice_element_open = """
<voice  name='{voiceName}'><prosody pitch='{pitch}Hz' rate ='{rate}%' volume='{volume}%'>
            """.strip().format(
                voiceName=self.voiceName,
                pitch=self._int_to_str(self.pitch),
                rate=self._int_to_str(self.rate),
                volume=self._int_to_str(self.volume),
            )
            voice_element_close = "</prosody></voice>"
            if (await self.get_voice())["Locale"][0:2].lower() == "ru":
                for k, v in {
                    "'": "ъ",
                }.items():
                    text = text.replace(k, v)
            if multivoices:
                text = await self.parse_multivoices(
                    text,
                    call_from_synthesize_function = True,
                    open_voice_tag_if_needed = voice_element_open,
                    close_voice_tag_if_needed = voice_element_close,
                    default_pitch = self.pitch,
                    default_rate = self.rate,
                    default_volume = self.volume,
                )
            if (await self.get_voice())["Locale"][0:2].lower() == "uk":
                for k, v in {"ў": "у", "Ў": "У"}.items():
                    text = text.replace(k, v)
            if (await self.get_voice())["Locale"][0:2].lower() == "ru":
                for k, v in {
                    "ў": "у",
                    "Ў": "У",
                    "і": "и",
                    "І": "И",
                    "ў": "у",
                    "Ў": "У",
                }.items():
                    text = text.replace(k, v)
            ssml = speak_element_open + voice_element_open + text + voice_element_close + speak_element_close
            ssml = re.sub(r"\<voice[^>]+\>\<prosody[^>]+>[\s\r\n]{0,}\</prosody\>\</voice>", "", ssml, flags = re.MULTILINE)
            await ws.send_str(
                self._build_request(
                    {
                        "X-RequestId": "586bb1cb2bbe2e68bb1e7617113bee75",
                        "Content-Type": "application/ssml+xml",
                        "Path": "ssml",
                    },
                    ssml,
                ).decode("UTF8")
            )
            f: Any = None
            while True:
                msg = await ws.receive()
                if (
                    f is not None
                    and msg.type == aiohttp.WSMsgType.text
                    and "json" in msg.data
                    and len(json.loads(self._extract_response(msg.data)[1])) == 0
                ) or (
                    msg.type == aiohttp.WSMsgType.closed
                    or msg.type == aiohttp.WSMsgType.error
                ):
                    await ws.close()
                    break
                if isinstance(msg.data, int):
                    await ws.close()
                    raise MSSpeechError(
                        self.errors.get(msg.data, "unknown error #" + str(msg.data))
                    )
                    break
                resp = self._extract_response(msg.data)
                if isinstance(resp[1], bytes):
                    if f is None:
                        if isinstance(filename_or_buffer, str):
                            f = await aiofiles.open(filename_or_buffer, "wb")
                        else:
                            f = filename_or_buffer
                    bc += await f.write(resp[1])
            if f is not None and isinstance(filename_or_buffer, str):
                await f.close()
            f = None
            return bc
