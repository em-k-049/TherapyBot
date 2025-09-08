import os
from typing import Optional

def translate_text(text: str, target_lang: str, source_lang: str = None) -> str:
    """Translate text using Google Translate API (stubbed)"""
    try:
        # TODO: Replace with actual Google Cloud Translate API
        # from google.cloud import translate_v2 as translate
        # translate_client = translate.Client()
        # result = translate_client.translate(text, target_language=target_lang, source_language=source_lang)
        # return result['translatedText']
        
        # Stub implementation with common translations
        translations = {
            'es': {
                'hello': 'hola',
                'help': 'ayuda',
                'thank you': 'gracias',
                'how are you': 'como estas',
                'i need help': 'necesito ayuda',
                'i feel sad': 'me siento triste',
                'goodbye': 'adios'
            },
            'fr': {
                'hello': 'bonjour',
                'help': 'aide',
                'thank you': 'merci',
                'how are you': 'comment allez-vous',
                'i need help': "j'ai besoin d'aide",
                'i feel sad': 'je me sens triste',
                'goodbye': 'au revoir'
            },
            'de': {
                'hello': 'hallo',
                'help': 'hilfe',
                'thank you': 'danke',
                'how are you': 'wie geht es dir',
                'i need help': 'ich brauche hilfe',
                'i feel sad': 'ich fühle mich traurig',
                'goodbye': 'auf wiedersehen'
            }
        }
        
        # Simple stub translation
        text_lower = text.lower().strip()
        if target_lang in translations and text_lower in translations[target_lang]:
            return translations[target_lang][text_lower]
        
        # Return original text with language indicator if no translation found
        return f"[{target_lang.upper()}] {text}"
        
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def detect_language(text: str) -> str:
    """Detect language of text (stubbed)"""
    try:
        # TODO: Replace with actual Google Cloud Translate API
        # from google.cloud import translate_v2 as translate
        # translate_client = translate.Client()
        # result = translate_client.detect_language(text)
        # return result['language']
        
        # Simple stub detection based on common words
        text_lower = text.lower()
        
        spanish_words = ['hola', 'gracias', 'ayuda', 'necesito', 'siento', 'triste']
        french_words = ['bonjour', 'merci', 'aide', 'besoin', 'sens', 'triste']
        german_words = ['hallo', 'danke', 'hilfe', 'brauche', 'fühle', 'traurig']
        
        if any(word in text_lower for word in spanish_words):
            return 'es'
        elif any(word in text_lower for word in french_words):
            return 'fr'
        elif any(word in text_lower for word in german_words):
            return 'de'
        
        return 'en'  # Default to English
        
    except Exception as e:
        print(f"Language detection error: {e}")
        return 'en'

def get_supported_languages() -> dict:
    """Get list of supported languages"""
    return {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese'
    }