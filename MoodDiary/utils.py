from googletrans import Translator

def translate_text(text):
    translator = Translator()
    translated = translator.translate(text, dest='en')
    return translated.text

def analyze_mood(text):
    lower = text.lower()
    if any(word in lower for word in ["sad", "depressed", "bad", "angry", "tired"]):
        return "Sad", "I'm here for you. Take a deep breath. Want to hear some uplifting quotes?"
    elif any(word in lower for word in ["happy", "joy", "excited", "good", "great"]):
        return "Happy", "That's awesome! Keep the good vibes going 🌟"
    else:
        return "Neutral", "Thanks for sharing. Stay balanced and take care!"
