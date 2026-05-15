import os
from openai import OpenAI
from core.api_config import APIConfig
from deep_translator import GoogleTranslator

class TranslationService:
    def __init__(self):
        config = APIConfig()
        self.client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key
        )
        self.model = config.model

    def translate(self, text):
        if not text.strip():
            return ""
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Translate the following segment into Thai, without additional explanation:\n\n {text}"
                    }
                ]
                ,temperature=0.1,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Translation API Error: {e}")
            return f"Error: {e}"


# class TranslationService:
#     def __init__(self):
#         self.translator = GoogleTranslator(source='en', target='th')

#     def translate(self, text):
#         if not text.strip():
#             return ""
#         try:
#             return self.translator.translate(text)
#         except Exception as e:
#             print(f"Translation Error: {e}")
#             return f"Error: {e}"
        