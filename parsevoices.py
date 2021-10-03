import html
import json
import re
with open("voicesplus.txt") as f: table = f.read()
table = table.replace("\r", "").replace("\n", "").replace("<code>", "").replace("</code>", "").replace("<sup>New</sup>", "")

json_voices_list = []
tbody = re.findall(r"<tbody>(.*?)</tbody>", table, re.M+re.I)[0]
trs = re.findall(r"<tr>(.*?)</tr>", tbody, re.M+re.I)

for tr in trs:
	tds = re.findall(r"<td>(.*?)</td>", tr, re.M+re.I)
	status = tds[4].split(",", 1)[0]
	locale = tds[1]
	name = tds[3].replace(locale+"-", "")
	json_voices_list.append({
		"Name":f"Microsoft Server Speech Text to Speech Voice ({locale}, {name})",
		"ShortName":f"{tds[3]}",
		"Gender":f"{tds[2]}",
		"Locale":locale,
		"FriendlyName":f"{name.replace('Neural', '')} - {tds[0]}",
		"SuggestedCodec": "audio-24khz-48kbitrate-mono-mp3",
		"Status":status
	})

with open("voices_list_plus.json", "w", encoding="UTF8") as w: json.dump(json_voices_list, w, indent=2, sort_keys=True)
print("Done!")
