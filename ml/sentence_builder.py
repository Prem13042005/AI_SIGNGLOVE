import pyttsx3

# Sentence Buffer
sentence_buffer = []

# Voice Engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Add Word
def add_word(word):

    word = word.upper()

    # Prevent duplicate consecutive words
    if sentence_buffer:

        if sentence_buffer[-1] == word:
            return

    sentence_buffer.append(word)

# Format Sentence
def format_sentence():

    if not sentence_buffer:
        return ""

    replacements = {

        "HELLO": "Hello",
        "MY": "my",
        "NAME": "name",
        "IS": "is",
        "OMKAR": "Omkar"
    }

    formatted_words = []

    for word in sentence_buffer:

        formatted_words.append(
            replacements.get(word, word.lower())
        )

    sentence = " ".join(formatted_words)

    # Capitalize first letter
    sentence = sentence[0].upper() + sentence[1:]

    # Add full stop
    if not sentence.endswith("."):
        sentence += "."

    return sentence

# Suggestions
def get_suggestions():

    suggestions_map = {

        ("HELLO",): ["MY"],

        ("HELLO", "MY"): ["NAME"],

        ("HELLO", "MY", "NAME"): ["IS"],

        ("HELLO", "MY", "NAME", "IS"): ["OMKAR"]
    }

    key = tuple(sentence_buffer)

    return suggestions_map.get(key, [])

# Speak Sentence
def speak_sentence(sentence):

    if sentence:

        engine.say(sentence)
        engine.runAndWait()

# Clear Sentence
def clear_sentence():

    sentence_buffer.clear()

# Get Current Buffer
def get_sentence_buffer():

    return sentence_buffer