"""
Cuneiform Unicode Library
This file contains a comprehensive collection of Unicode Cuneiform symbols
organized by categories for use in the English to Cuneiform converter.
"""

# Main Cuneiform symbols (common words and concepts)
cuneiform_common = {
    "water": "𒀀",  # U+12000 CUNEIFORM SIGN A
    "sky": "𒀭",    # U+1202D CUNEIFORM SIGN AN
    "house": "𒂍",  # U+12088 CUNEIFORM SIGN E2
    "mountain": "𒆳", # U+121B3 CUNEIFORM SIGN KUR
    "god": "𒀭",     # U+1202D CUNEIFORM SIGN AN (same as sky, context matters)
    "man": "𒇽",     # U+121FD CUNEIFORM SIGN LU2
    "woman": "𒊩",   # U+122A9 CUNEIFORM SIGN MUNUS
    "mouth": "𒅗",   # U+12157 CUNEIFORM SIGN KA
    "sun": "𒌓",     # U+12313 CUNEIFORM SIGN UD
    "moon": "𒌍",    # U+1230D CUNEIFORM SIGN ITUD
    "ox": "𒄞",      # U+1211E CUNEIFORM SIGN GUD
    "barley": "𒊺",  # U+122BA CUNEIFORM SIGN SHE
    "fish": "𒄩",    # U+12129 CUNEIFORM SIGN HA
    "bird": "𒄷",    # U+12137 CUNEIFORM SIGN MUŠEN
    "to_go": "𒁺",   # U+1207A CUNEIFORM SIGN DU
    "city": "𒌷",    # U+12337 CUNEIFORM SIGN URU
    "field": "𒃷",   # U+120F7 CUNEIFORM SIGN GAN2
    "king": "𒈗",    # U+12217 CUNEIFORM SIGN LUGAL
    "arrow": "𒉿",   # U+1227F CUNEIFORM SIGN TI
    "star": "𒀯",    # U+1202F CUNEIFORM SIGN MUL
    "earth": "𒆠",   # U+121A0 CUNEIFORM SIGN KI
    "temple": "𒂍𒀭", # U+12088 U+1202D CUNEIFORM SIGN E2 + AN
    "food": "𒉺",    # U+1227A CUNEIFORM SIGN NINDA2
    "drink": "𒅗𒀀", # U+12157 U+12000 CUNEIFORM SIGN KA + A
    "fire": "𒉈",    # U+12248 CUNEIFORM SIGN NE
    "wood": "𒄑",    # U+12111 CUNEIFORM SIGN GIŠ
    "stone": "𒎎",   # U+1238E CUNEIFORM SIGN NA4
    "silver": "𒆬",  # U+121AC CUNEIFORM SIGN KU3 BABBAR
    "gold": "𒆬𒄀",  # U+121AC U+12100 CUNEIFORM SIGN KU3 SIG17
    "copper": "𒍏",  # U+1233F CUNEIFORM SIGN URUDA
    "river": "𒀀𒇉",  # U+12000 U+121C9 CUNEIFORM SIGN A + ID2
    "boat": "𒈠𒀀",   # U+12220 U+12000 CUNEIFORM SIGN MA2
    "plow": "𒄑𒀳",   # U+12111 U+12033 CUNEIFORM SIGN GIŠ + APIN
    "sheep": "𒇬",    # U+121EC CUNEIFORM SIGN LU
    "goat": "𒄩𒇻",   # U+12129 U+121FB CUNEIFORM SIGN UD5
    "dog": "𒌨",      # U+12328 CUNEIFORM SIGN UR
    "lion": "𒌨𒈠𒄭",  # U+12328 U+12220 U+12137 CUNEIFORM SIGN UR + MAH
    "horse": "𒀲𒆳𒊏", # U+12032 U+121B3 U+1228F CUNEIFORM SIGN ANŠE + KUR + RA
    "donkey": "𒀲",   # U+12032 CUNEIFORM SIGN ANŠE
    "pig": "𒍚",      # U+1235A CUNEIFORM SIGN ŠAH2
    "grain": "𒊺",    # U+122BA CUNEIFORM SIGN ŠE
    "bread": "𒌖",    # U+12316 CUNEIFORM SIGN NINDA
    "beer": "𒃻",     # U+120FB CUNEIFORM SIGN KAŠ
    "wine": "𒃻𒀭",   # U+120FB U+1202D CUNEIFORM SIGN GEŠTIN
    "oil": "𒉌",      # U+1224C CUNEIFORM SIGN I3
    "honey": "𒇻𒀭",  # U+121FB U+1202D CUNEIFORM SIGN LAL3
    "milk": "𒄀",     # U+12100 CUNEIFORM SIGN GA
    "father": "𒀀𒁀",  # U+12000 U+12040 CUNEIFORM SIGN AD
    "mother": "𒀀𒈠",  # U+12000 U+12220 CUNEIFORM SIGN AMA
    "son": "𒌉",      # U+12329 CUNEIFORM SIGN DUMU
    "daughter": "𒌉𒊩", # U+12329 U+122A9 CUNEIFORM SIGN DUMU + MUNUS
    "brother": "𒋀𒋡", # U+122C0 U+122E1 CUNEIFORM SIGN ŠEŠ
    "sister": "𒉡𒊩",  # U+12261 U+122A9 CUNEIFORM SIGN NIN9
    "name": "𒈬",     # U+1222C CUNEIFORM SIGN MU
    "hand": "𒋗",     # U+122D7 CUNEIFORM SIGN ŠU
    "foot": "𒄊",     # U+1210A CUNEIFORM SIGN GIR3
    "head": "𒊕",     # U+12295 CUNEIFORM SIGN SAG
    "eye": "𒄿𒄀",    # U+1213F U+12100 CUNEIFORM SIGN IGI
    "ear": "𒄀𒋗",    # U+12100 U+122D7 CUNEIFORM SIGN GEŠTUG
    "heart": "𒋗𒀀",   # U+122D7 U+12000 CUNEIFORM SIGN ŠA3
    "blood": "𒌓𒊬",   # U+12313 U+122AC CUNEIFORM SIGN MUD
    "bone": "𒄀𒄑",    # U+12100 U+12111 CUNEIFORM SIGN GIR2
    "day": "𒌓",      # U+12313 CUNEIFORM SIGN UD
    "night": "𒄀𒄿",   # U+12100 U+1213F CUNEIFORM SIGN GE6
    "year": "𒈬",     # U+1222C CUNEIFORM SIGN MU
    "month": "𒌗",    # U+12317 CUNEIFORM SIGN ITI
    "spring": "𒌓𒊬",  # U+12313 U+122AC CUNEIFORM SIGN UD + SIG
    "summer": "𒌓𒈪",  # U+12313 U+12222 CUNEIFORM SIGN UD + NE
    "autumn": "𒌓𒋆",  # U+12313 U+122C6 CUNEIFORM SIGN UD + ŠU2
    "winter": "𒌓𒂵",  # U+12313 U+120B5 CUNEIFORM SIGN UD + EN
    "north": "𒀭𒈾",   # U+1202D U+1223A CUNEIFORM SIGN IM1
    "south": "𒀭𒋢",   # U+1202D U+122E2 CUNEIFORM SIGN IM3
    "east": "𒀭𒌓𒀀",   # U+1202D U+12313 U+12000 CUNEIFORM SIGN IM + UD + E3
    "west": "𒀭𒌓𒋗",   # U+1202D U+12313 U+122D7 CUNEIFORM SIGN IM + UD + ŠU4
    "one": "𒁹",      # U+12079 CUNEIFORM SIGN AŠ
    "two": "𒈫",      # U+1222B CUNEIFORM SIGN MIN
    "three": "𒐈",    # U+12408 CUNEIFORM NUMERIC SIGN THREE DISH
    "four": "𒐉",     # U+12409 CUNEIFORM NUMERIC SIGN FOUR DISH
    "five": "𒐊",     # U+1240A CUNEIFORM NUMERIC SIGN FIVE DISH
    "six": "𒐋",      # U+1240B CUNEIFORM NUMERIC SIGN SIX DISH
    "seven": "𒐌",    # U+1240C CUNEIFORM NUMERIC SIGN SEVEN DISH
    "eight": "𒐍",    # U+1240D CUNEIFORM NUMERIC SIGN EIGHT DISH
    "nine": "𒐎",     # U+1240E CUNEIFORM NUMERIC SIGN NINE DISH
    "ten": "𒌋",      # U+1230B CUNEIFORM SIGN U
    "twenty": "𒌋𒌋",  # U+1230B U+1230B CUNEIFORM SIGN U + U
    "thirty": "𒌍𒐈",  # U+1230D U+12408 CUNEIFORM SIGN ITUD + THREE
    "forty": "𒐏",    # U+1240F CUNEIFORM NUMERIC SIGN FOUR U
    "fifty": "𒐐",    # U+12410 CUNEIFORM NUMERIC SIGN FIVE U
    "sixty": "𒐑",    # U+12411 CUNEIFORM NUMERIC SIGN SIX U
    "hundred": "𒈯",  # U+1222F CUNEIFORM SIGN ME
    "thousand": "𒄭𒆸", # U+12137 U+121B8 CUNEIFORM SIGN LIM
}

# Cuneiform numbers and punctuation
cuneiform_numbers = {
    "1": "𒐕",    # U+12415 CUNEIFORM NUMERIC SIGN ONE GESH2
    "2": "𒐖",    # U+12416 CUNEIFORM NUMERIC SIGN TWO GESH2
    "3": "𒐗",    # U+12417 CUNEIFORM NUMERIC SIGN THREE GESH2
    "4": "𒐘",    # U+12418 CUNEIFORM NUMERIC SIGN FOUR GESH2
    "5": "𒐙",    # U+12419 CUNEIFORM NUMERIC SIGN FIVE GESH2
    "6": "𒐚",    # U+1241A CUNEIFORM NUMERIC SIGN SIX GESH2
    "7": "𒐛",    # U+1241B CUNEIFORM NUMERIC SIGN SEVEN GESH2
    "8": "𒐜",    # U+1241C CUNEIFORM NUMERIC SIGN EIGHT GESH2
    "9": "𒐝",    # U+1241D CUNEIFORM NUMERIC SIGN NINE GESH2
    "10": "𒌋",   # U+1230B CUNEIFORM SIGN U
    "20": "𒌋𒌋", # U+1230B U+1230B CUNEIFORM SIGN U + U
    "30": "𒌋𒌋𒌋", # U+1230B U+1230B U+1230B CUNEIFORM SIGN U + U + U
    "40": "𒐏",   # U+1240F CUNEIFORM NUMERIC SIGN FOUR U
    "50": "𒐐",   # U+12410 CUNEIFORM NUMERIC SIGN FIVE U
    "60": "𒐑",   # U+12411 CUNEIFORM NUMERIC SIGN SIX U
    "70": "𒐒",   # U+12412 CUNEIFORM NUMERIC SIGN SEVEN U
    "80": "𒐓",   # U+12413 CUNEIFORM NUMERIC SIGN EIGHT U
    "90": "𒐔",   # U+12414 CUNEIFORM NUMERIC SIGN NINE U
    "100": "𒈯",  # U+1222F CUNEIFORM SIGN ME
    "1000": "𒄭𒆸", # U+12137 U+121B8 CUNEIFORM SIGN LIM
    "1/2": "𒑔",  # U+12454 CUNEIFORM NUMERIC SIGN FIVE BAN2
    "1/3": "𒑝",  # U+1245D CUNEIFORM NUMERIC SIGN ONE THIRD VARIANT FORM A
    "2/3": "𒑞",  # U+1245E CUNEIFORM NUMERIC SIGN TWO THIRDS VARIANT FORM A
    "1/4": "𒑠",  # U+12460 CUNEIFORM NUMERIC SIGN ONE QUARTER ASH
    "1/8": "𒑟",  # U+1245F CUNEIFORM NUMERIC SIGN ONE EIGHTH ASH
    "5/6": "𒑜",  # U+1245C CUNEIFORM NUMERIC SIGN FIVE SIXTHS DISH
}

# Early Dynastic Cuneiform symbols (additional symbols)
cuneiform_early_dynastic = {
    "temple_complex": "𒒀",  # U+12480 CUNEIFORM SIGN AB TIMES NUN TENU
    "offering": "𒒁",        # U+12481 CUNEIFORM SIGN AB TIMES SHU2
    "ritual": "𒒂",          # U+12482 CUNEIFORM SIGN AD TIMES ESH2
    "sacrifice": "𒒃",       # U+12483 CUNEIFORM SIGN BAD TIMES DISH TENU
    "agriculture": "𒒄",     # U+12484 CUNEIFORM SIGN BAHAR2 TIMES AB2
    "harvest": "𒒅",         # U+12485 CUNEIFORM SIGN BAHAR2 TIMES NI
    "irrigation": "𒒆",      # U+12486 CUNEIFORM SIGN BAHAR2 TIMES ZA
    "storage": "𒒇",         # U+12487 CUNEIFORM SIGN BU OVER BU TIMES NA2
    "tax": "𒒈",             # U+12488 CUNEIFORM SIGN DA TIMES TAK4
    "foreign_land": "𒒉",    # U+12489 CUNEIFORM SIGN DAG TIMES KUR
    "measurement": "𒒊",     # U+1248A CUNEIFORM SIGN DIM TIMES IGI
    "boundary": "𒒋",        # U+1248B CUNEIFORM SIGN DIM TIMES U U U
    "time_period": "𒒌",     # U+1248C CUNEIFORM SIGN DIM2 TIMES UD
    "transport": "𒒍",       # U+1248D CUNEIFORM SIGN DUG TIMES ANSHE
    "container": "𒒎",       # U+1248E CUNEIFORM SIGN DUG TIMES ASH
    "vessel": "𒒏",          # U+1248F CUNEIFORM SIGN DUG TIMES ASH AT LEFT
    "pottery": "𒒐",         # U+12490 CUNEIFORM SIGN DUG TIMES DIN
    "basket": "𒒑",          # U+12491 CUNEIFORM SIGN DUG TIMES DUN
    "tool": "𒒒",            # U+12492 CUNEIFORM SIGN DUG TIMES ERIN2
    "weapon": "𒒓",          # U+12493 CUNEIFORM SIGN DUG TIMES GA
    "textile": "𒒔",         # U+12494 CUNEIFORM SIGN DUG TIMES GI
    "garment": "𒒕",         # U+12495 CUNEIFORM SIGN DUG TIMES GIR2 GUNU
    "ornament": "𒒖",        # U+12496 CUNEIFORM SIGN DUG TIMES GISH
    "jewelry": "𒒗",         # U+12497 CUNEIFORM SIGN DUG TIMES HA
    "ceremony": "𒒘",        # U+12498 CUNEIFORM SIGN DUG TIMES HI
    "festival": "𒒙",        # U+12499 CUNEIFORM SIGN DUG TIMES IGI GUNU
    "journey": "𒒚",         # U+1249A CUNEIFORM SIGN DUG TIMES KASKAL
    "expedition": "𒒛",      # U+1249B CUNEIFORM SIGN DUG TIMES KUR
    "trade": "𒒜",           # U+1249C CUNEIFORM SIGN DUG TIMES KUSHU2
    "merchant": "𒒝",        # U+1249D CUNEIFORM SIGN DUG TIMES KUSHU2 PLUS KASKAL
    "scribe": "𒒞",          # U+1249E CUNEIFORM SIGN DUG TIMES LAK-020
    "writing": "𒒟",         # U+1249F CUNEIFORM SIGN DUG TIMES LAM
    "record": "𒒠",          # U+124A0 CUNEIFORM SIGN DUG TIMES LAM TIMES KUR
    "account": "𒒡",         # U+124A1 CUNEIFORM SIGN DUG TIMES LUH PLUS GISH
    "official": "𒒢",        # U+124A2 CUNEIFORM SIGN DUG TIMES MASH
    "ruler": "𒒣",           # U+124A3 CUNEIFORM SIGN DUG TIMES MES
    "governor": "𒒤",        # U+124A4 CUNEIFORM SIGN DUG TIMES MI
    "priest": "𒒥",          # U+124A5 CUNEIFORM SIGN DUG TIMES NI
    "priestess": "𒒦",       # U+124A6 CUNEIFORM SIGN DUG TIMES PI
    "servant": "𒒧",         # U+124A7 CUNEIFORM SIGN DUG TIMES SHE
    "slave": "𒒨",           # U+124A8 CUNEIFORM SIGN DUG TIMES SI GUNU
    "palace": "𒒩",          # U+124A9 CUNEIFORM SIGN E2 TIMES KUR
    "fortress": "𒒪",        # U+124AA CUNEIFORM SIGN E2 TIMES PAP
}

# Merge all dictionaries to create a comprehensive library
cuneiform_library = {**cuneiform_common, **cuneiform_numbers, **cuneiform_early_dynastic}

def english_to_cuneiform(text):
    """
    Convert English text to Cuneiform symbols.
    
    Args:
        text (str): English text to convert
        
    Returns:
        str: Converted Cuneiform text
    """
    words = text.lower().split()
    cuneiform_output = ""
    
    for word in words:
        if word in cuneiform_library:
            cuneiform_output += cuneiform_library[word] + " "
        else:
            # Check if the word is a number
            if word.isdigit():
                # For multi-digit numbers, convert each digit
                for digit in word:
                    if digit in cuneiform_numbers:
                        cuneiform_output += cuneiform_numbers[digit]
                cuneiform_output += " "
            else:
                cuneiform_output += "? "  # unknown word
    
    return cuneiform_output.strip()

# Example usage
if __name__ == "__main__":
    english_text = input("Enter English text: ")
    cuneiform_text = english_to_cuneiform(english_text)
    print(cuneiform_text)
