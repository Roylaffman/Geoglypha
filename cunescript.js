// Cuneiform Library - Contains all the mappings from English words to Cuneiform symbols
const cuneiformLibrary = {
    // Common words and concepts
    "water": "𒀀",
    "sky": "𒀭",
    "house": "𒂍",
    "mountain": "𒆳",
    "god": "𒀭",
    "man": "𒇽",
    "woman": "𒊩",
    "mouth": "𒅗",
    "sun": "𒌓",
    "moon": "𒌍",
    "ox": "𒄞",
    "barley": "𒊺",
    "fish": "𒄩",
    "bird": "𒄷",
    "to_go": "𒁺",
    "city": "𒌷",
    "field": "𒃷",
    "king": "𒈗",
    "arrow": "𒉿",
    "star": "𒀯",
    "earth": "𒆠",
    "temple": "𒂍𒀭",
    "food": "𒉺",
    "drink": "𒅗𒀀",
    "fire": "𒉈",
    "wood": "𒄑",
    "stone": "𒎎",
    "silver": "𒆬",
    "gold": "𒆬𒄀",
    "copper": "𒍏",
    "river": "𒀀𒇉",
    "boat": "𒈠𒀀",
    "plow": "𒄑𒀳",
    "sheep": "𒇬",
    "goat": "𒄩𒇻",
    "dog": "𒌨",
    "lion": "𒌨𒈠𒄭",
    "horse": "𒀲𒆳𒊏",
    "donkey": "𒀲",
    "pig": "𒍚",
    "grain": "𒊺",
    "bread": "𒌖",
    "beer": "𒃻",
    "wine": "𒃻𒀭",
    "oil": "𒉌",
    "honey": "𒇻𒀭",
    "milk": "𒄀",
    "father": "𒀀𒁀",
    "mother": "𒀀𒈠",
    "son": "𒌉",
    "daughter": "𒌉𒊩",
    "brother": "𒋀𒋡",
    "sister": "𒉡𒊩",
    "name": "𒈬",
    "hand": "𒋗",
    "foot": "𒄊",
    "head": "𒊕",
    "eye": "𒄿𒄀",
    "ear": "𒄀𒋗",
    "heart": "𒋗𒀀",
    "blood": "𒌓𒊬",
    "bone": "𒄀𒄑",
    "day": "𒌓",
    "night": "𒄀𒄿",
    "year": "𒈬",
    "month": "𒌗",
    "spring": "𒌓𒊬",
    "summer": "𒌓𒈪",
    "autumn": "𒌓𒋆",
    "winter": "𒌓𒂵",
    "north": "𒀭𒈾",
    "south": "𒀭𒋢",
    "east": "𒀭𒌓𒀀",
    "west": "𒀭𒌓𒋗",
    
    // Numbers
    "one": "𒁹",
    "two": "𒈫",
    "three": "𒐈",
    "four": "𒐉",
    "five": "𒐊",
    "six": "𒐋",
    "seven": "𒐌",
    "eight": "𒐍",
    "nine": "𒐎",
    "ten": "𒌋",
    "twenty": "𒌋𒌋",
    "thirty": "𒌍𒐈",
    "forty": "𒐏",
    "fifty": "𒐐",
    "sixty": "𒐑",
    "hundred": "𒈯",
    "thousand": "𒄭𒆸",
    
    // Numeric digits
    "1": "𒐕",
    "2": "𒐖",
    "3": "𒐗",
    "4": "𒐘",
    "5": "𒐙",
    "6": "𒐚",
    "7": "𒐛",
    "8": "𒐜",
    "9": "𒐝",
    "0": "𒌋𒌋",
    
    // Additional words to find symbols
    // potential source https://en.wikipedia.org/wiki/Cuneiform_(Unicode_block)
    "temple_complex": "𒒀",
    "offering": "𒒁",
    "ritual": "𒒂",
    "sacrifice": "𒒃",
    "agriculture": "𒒄",
    "harvest": "𒒅",
    "irrigation": "𒒆",
    "storage": "𒒇",
    "tax": "𒒈",
    "foreign_land": "𒒉",
    "measurement": "𒒊",
    "boundary": "𒒋",
    "time_period": "𒒌",
    "transport": "𒒍",
    "container": "𒒎",
    "vessel": "𒒏",
    "pottery": "𒒐",
    "basket": "𒒑",
    "tool": "𒒒",
    "weapon": "𒒓",
    "textile": "𒒔",
    "garment": "𒒕",
    "ornament": "𒒖",
    "jewelry": "𒒗",
    "ceremony": "𒒘",
    "festival": "𒒙",
    "journey": "𒒚",
    "expedition": "𒒛",
    "trade": "𒒜",
    "merchant": "𒒝",
    "scribe": "𒒞",
    "writing": "𒒟",
    "record": "𒒠",
    "account": "𒒡",
    "official": "𒒢",
    "ruler": "𒒣",
    "governor": "𒒤",
    "priest": "𒒥",
    "priestess": "𒒦",
    "servant": "𒒧",
    "slave": "𒒨",
    "palace": "𒂍",
    "fortress": "𒒪",
    // You
    "you": "𒋗", 
    // Common phrases
    "good day": "𒌓 𒄭",
    "thank you": "𒋗𒀀 𒀭",
    "welcome": "𒁺 𒂍",
    "farewell": "𒋗𒀀 𒁺",
    "great king": "𒈗 𒃲",
    "holy temple": "𒂍𒀭 𒆠",
    "mighty warrior": "𒇽 𒄷",
    "fertile land": "𒆠 𒊺",
    "sacred water": "𒀀 𒀭",
    "royal palace": "𒂍 𒈗",
    "ancient city": "𒌷 𒈬",
    "divine protection": "𒀭 𒋗",
    "eternal life": "𒌓 𒌓",

    //verbs - need to break down and add most common verb in english 
    "to speak, to say": "𒂊",
    "to water, to irrigate": "𒀀𒇉",
    "to be two, to double": "𒈫",
    "to speak, to say": "𒅗",
    "to rise, to raise": "𒍣",
    "to ride, to mount": "𒌋",
    "to send, to throw": "𒊒",
    "to grow, to sprout": "𒈬",
    "to return, to restore": "𒄀",
    "to release, to free": "𒁕",
    "to place, to set": "𒆘",
    "to go, to walk": "𒁵",
    "to found, to establish": "𒌷 𒈬",
    "to bring, to carry": "𒌆",
    "to bring, to lead": "𒅔",
    "to make, to do": "𒀀𒇉",
    "to die, to kill": "𒍑",
    "to equal, to compare": "𒊓",
    "to lie down, to sleep": "𒈖",
    "to lift, to carry": "𒅏"  
};

// Function to convert English text to Cuneiform
function englishToCuneiform(text) {
    const words = text.toLowerCase().split(/\s+/);
    let cuneiformOutput = "";
    
    for (const word of words) {
        // Check if the word exists in our library
        if (cuneiformLibrary[word]) {
            cuneiformOutput += cuneiformLibrary[word] + " ";
        } 
        // Check if it's a number
        else if (/^\d+$/.test(word)) {
            // For multi-digit numbers, convert each digit
            for (const digit of word) {
                if (cuneiformLibrary[digit]) {
                    cuneiformOutput += cuneiformLibrary[digit];
                }
            }
            cuneiformOutput += " ";
        }
        // Check for underscores (for compound words like "to_go")
        else if (word.includes('_')) {
            if (cuneiformLibrary[word]) {
                cuneiformOutput += cuneiformLibrary[word] + " ";
            } else {
                cuneiformOutput += "? ";
            }
        }
        // Unknown word
        else {
            cuneiformOutput += "? ";
        }
    }
    
    return cuneiformOutput.trim();
}

// DOM elements
const englishInput = document.getElementById('english-input');
const convertBtn = document.getElementById('convert-btn');
const cuneiformOutput = document.getElementById('cuneiform-output');
const copyBtn = document.getElementById('copy-btn');
const copyMessage = document.getElementById('copy-message');

// Event listener for convert button
convertBtn.addEventListener('click', () => {
    const englishText = englishInput.value.trim();
    if (englishText) {
        const cuneiformText = englishToCuneiform(englishText);
        cuneiformOutput.textContent = cuneiformText;
    } else {
        cuneiformOutput.textContent = '';
    }
});

// Event listener for copy button
copyBtn.addEventListener('click', () => {
    const cuneiformText = cuneiformOutput.textContent;
    if (cuneiformText) {
        navigator.clipboard.writeText(cuneiformText)
            .then(() => {
                // Show the copied message
                copyMessage.classList.remove('hidden');
                
                // Hide the message after 2 seconds
                setTimeout(() => {
                    copyMessage.classList.add('hidden');
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
            });
    }
});

// Event listener for input to enable real-time conversion (optional)
englishInput.addEventListener('input', () => {
    const englishText = englishInput.value.trim();
    if (englishText) {
        const cuneiformText = englishToCuneiform(englishText);
        cuneiformOutput.textContent = cuneiformText;
    } else {
        cuneiformOutput.textContent = '';
    }
});

// Initialize with example text
window.addEventListener('DOMContentLoaded', () => {
    englishInput.value = "king temple water sky mountain";
    const cuneiformText = englishToCuneiform(englishInput.value);
    cuneiformOutput.textContent = cuneiformText;
});
