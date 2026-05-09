from deep_translator import GoogleTranslator

class TranslationService:
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='th')

    def translate(self, text):
        return self.translator.translate(text)