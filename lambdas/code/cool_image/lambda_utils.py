import boto3

translate = boto3.client("translate")

def translate_from_english(text, lang):
    if lang == "en":
        return text

    # Call the TranslateText API to translate the text to English
    translation_response = translate.translate_text(
        Text=text, SourceLanguageCode="en", TargetLanguageCode=lang
    )

    # Extract the translated text from the response
    translated_text = translation_response["TranslatedText"]

    return translated_text

def translate_to_en(text):
    
    # Call the TranslateText API to translate the text to English
    translation_response = translate.translate_text(
        Text=text, SourceLanguageCode="auto", TargetLanguageCode="en"
    )

    # Extract the translated text from the response
    translated_text = translation_response["TranslatedText"]
    dominant_language = translation_response["SourceLanguageCode"]
    print(translation_response)

    return translated_text, dominant_language