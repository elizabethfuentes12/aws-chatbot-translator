import json
import lex_utils as lex_lib
import boto3

client_comprehend = boto3.client('comprehend')
client_translate = boto3.client('translate')


def detetct_language (text):
    response = client_comprehend.detect_dominant_language(
        Text=text
    )
    return response['Languages'][0]['LanguageCode']

def translate_text (text,language_in,language_out):
    response = client_translate.translate_text(
    Text=text,
    SourceLanguageCode=language_in,
    TargetLanguageCode=language_out,
  
)
    return response['TranslatedText'] 


def lambda_handler(event, context):
    # TODO implement
    print(event)
    
    interpretations = event['interpretations']
    intent_name = interpretations[0]['intent']['name']
    intent = lex_lib.get_intent(event)
    active_contexts = lex_lib.get_active_contexts(event)
    session_attributes = lex_lib.get_session_attributes(event)
    previous_slot_to_elicit = session_attributes.get("previous_slot_to_elicit")
    
    if intent_name == 'TranslateIntent':
        print(intent_name)
        language_out = lex_lib.get_slot("language_out",intent)
        text_to_translate = lex_lib.get_slot("text_to_translate",intent)
        
        if language_out == None:
            return lex_lib.delegate(active_contexts, session_attributes, intent)
            
        if (text_to_translate == None) and (previous_slot_to_elicit != "text_to_translate") :
            response = "What text do you want to translate?"
            messages =  [{'contentType': 'PlainText', 'content': response}]
            return lex_lib.elicit_slot("text_to_translate", active_contexts, session_attributes, intent, messages)
       
        if previous_slot_to_elicit == "text_to_translate": 
            text_to_translate = event["inputTranscript"]
            language_in = detetct_language (text_to_translate)
    
        print(language_out,text_to_translate,language_in)
        
        text_ready = translate_text(text_to_translate,language_in,language_out)
        response = f"The translate text is: {text_ready}. \nAnything else?"
        messages =  [{'contentType': 'PlainText', 'content': response}]
        print(lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages))
        
        return lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages)
        