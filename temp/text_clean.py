from re import sub, UNICODE
from requests import get


def emojis() -> str:
    page = get(
        "https://www.unicode.org/Public/UCD/latest/ucd/emoji/emoji-data.txt")
    lines = page.text.split("\n")

    blacklist = [  # blacklist of element who are not really emojis
        "number sign",
        "asterisk",
        "digit zero..digit nine",
        "copyright",
        "registered",
        "double exclamation mark",
        "exclamation question mark",
        "trade mark",
        "information"
    ]

    unicodes = []
    extendedEmoji = {}
    for line in lines:  # check all lines
        # ignores comment lines and blank lines
        if not line.startswith("#") and len(line) > 0:
            # check if the emoji isn't in the blacklist
            if line.split(')')[1].strip() not in blacklist:
                # recovery of the first column
                temp = f"{line.split(';')[0]}".strip()
                if ".." in temp:  # if it is a "list" of emojis, adding to a dict
                    extendedEmoji[temp.split("..")[0]] = temp.split("..")[1]
                else:
                    unicodes.append(temp)
    # removal of duplicates and especially of extra spaces
    unicodes = list(set(unicodes) - {""})

    def _uChar(string: str):  # choice between \u and \U in addition of the "0" to complete the code
        stringLen = len(string)
        if stringLen > 7:  # Can't be more than 7 anyways
            raise Exception(f"{string} is too long! ({stringLen})")
        u, totalLong = "U", 7  # Should be 7 characters long if it is a capital U
        if stringLen < 4:  # 4 characters long if smaller than 4
            u, totalLong = "u", 4  # Should be 4 characters long if it is a lowercase u
        resultat = ""
        while len(f"{resultat}{string}") <= totalLong:  # Adding the 0
            resultat += "0"
        # Return the right "U" with the right number of 0
        return f"\{u}{resultat}"

    for i in range(0, len(unicodes)):  # add unicode syntax to the list
        unicodes[i] = f"{_uChar(unicodes[i])}{unicodes[i]}"

    for mot in extendedEmoji.items():  # add unicode syntax to the dict
        extendedEmoji[mot[0]] = f"{_uChar(mot[1])}{mot[1]}"
        temp = f"{_uChar(mot[0])}{mot[0]}-{extendedEmoji[mot[0]]}"
        if temp not in unicodes:  # if not already in the list
            unicodes.append(temp)  # add the item to the list

    resultat = "["
    for code in unicodes:  # conversion of the list into a string with | to separate all the emojis
        resultat += f"{code}|"

    return f"{resultat[:-1]}]+"


# For testing, to be removed
string = "hello 😂"
print(
    f"String: {string}\nWithout Emojis: {sub(emojis(), '', string, flags = UNICODE)}")

text_lists = [
    "RT @milinchav: แอบแวะมาแปะเด็กยิ้มหวานตาแป๋ว🥺💖 #ChampooCGM48 https://t.co/BvHmSVsufQ",
    "RT @Ponlapatz: ยิ่งดูฟุตเทจ ยิ่งดูรูป ยิ่งเห็นว่าแชมพูเก่งขึ้นมากๆ\nดีใจ ปลื้มปริ่ม 🥺\n🌲🌲 #ChampooCGM48 🌲🌲\ngood night na~ https://t.co/lPTmDq…",
    "RT @OZONE_48: พิออมรักทุกคนค่ะ...🥰\n\nFull Album : https://t.co/E15UZOznVM\n\n#AomCGM48 #CGM48 https://t.co/aaeD8JVvVD",
    "RT @twskr41: (˗ˋˏ ♡ ˎˊ˗)\n            :\n            :\n            :    🦖 𝗚𝗼𝗼𝗱𝗡𝗶𝗴𝗵𝘁 💗\n      _∩ﾊ   ﾊ ＿_\n\u3000  |( ֊  ̫ ֊   ) |\n   /⌒⌒⌒∪⌒/|\n  /⌒⌒⌒⌒…",
    "RT @betelgm149: เป็นน่ารักไปหมดเลยง่าาา น่าย้ากจุ๋งจิ๋ง 🥺✨ #MarminkCGM48 https://t.co/nj93U32lYt",
    "RT @4fisthegod: วันนี้แองเจิ้ลเก่งมาก ตอบคำถามได้เยอะมากเลยย แถมน่ารักมากๆด้วย คืนนี้หลับฝันดีนะคะคนเก่ง ไน้ไน้!🌟\n\n#AngelCGM48 https://t.co…",
    "RT @sita_cgm48THFC: [#iAM48OfficialApplication] —📱\n\nจริง ๆ แล้วผมเป็นคนเพิ่งตื่น \n\n🖱 https://t.co/6TWamRIPvl\n\n#CGM48 #SitaCGM48 #STiAMalert…",
    "RT @BeWithMarmink: ต้าวมามิ้งค์ของพี่เนยเสียอาการเยยค่า ขอขิงนิดนึงเน้อะทุกคน เพราะพี่เนยน่าย้ากกก🥺✨ w/ #NoeyBNK48 #MarminkCGM48 https://t.…"
]

for i in range(len(text_lists)):
    text = text_lists[i]
    print('='*100)
    print('='*100)
    print(text)
    print('-'*100)
    text = sub(emojis(), '', text_lists[i], flags=UNICODE)
    print(text)
