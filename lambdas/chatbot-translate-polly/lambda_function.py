import boto3
import os
import time
import logging
import json
import lex_utils as lex
import internal_utils as utils

import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

region_name = os.environ.get('ENV_REGION_NAME')
bueket_key = os.environ.get('BUCKET_KEY')
bucket_name = os.environ.get('BUCKET_NAME')

language_code = dict( [ ('es','spanish'), ('pt','portuguese'), ('it','italian'), ('fr','french'),('en','english') ] )
language_en = dict( [ ('spanish', 'es'), ('portuguese', 'pt-PT'), ('italian', 'it'), ('french', 'fr'),('english', 'en') ] )
to_polly_voice = dict( [ ('en', 'Amy'), ('es', 'Conchita'), ('fr', 'Chantal'), ('pt-PT', 'Cristiano'),('it', 'Giorgio') ] )
to_polly_language = dict( [ ('en', 'en-US'), ('es', 'es-US'), ('fr', 'fr-FR'), ('pt-PT' , 'pt-BR'),('it', 'it-IT') ] )


client_comprehend = boto3.client('comprehend')
client_translate = boto3.client('translate')
client_polly = boto3.client('polly')

# Create an S3 client
s3_client = boto3.client('s3')

    
def smart_kendra(intent_request):
    print("intent_request: ",intent_request )
    
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
    
    source = intent_request['invocationSource']
    text_to_translate = intent_request['inputTranscript']
    active_contexts =  lex.get_active_contexts(intent_request)
    session_attributes = intent_request['sessionState']['sessionAttributes']
    intent = intent_request['interpretations'][0]["intent"]
    
    text = intent_request["interpretations"][0]["intent"]["slots"]["text"]
    language = intent_request["interpretations"][0]["intent"]["slots"]["language"]
    trasnlate = intent_request["interpretations"][0]["intent"]["slots"]["trasnlate"]


    print("\nSearch results for text_to_translate: " + text_to_translate + "\n")

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        
        if language is None: 
            slotToElicit = "language"
         
            state = 'ReadyForFulfillment'
            text = text_to_translate
            response_dominant_language = client_comprehend.detect_dominant_language(
                            Text= text_to_translate
                        )
            
            dominant_language = language_code[response_dominant_language["Languages"][0]["LanguageCode"]]
            confidence = response_dominant_language["Languages"][0]["Score"]
            
            print("\nSearch results for query: " + dominant_language + "\n")
            
         
            response_chat = f" The dominant language of the text is: {dominant_language}, with a the level of confidence: {confidence} , \n \n What language do you want to translate? ".format(dominant_language,confidence)
            print(response_chat)
         
            intent = lex.set_slot("trasnlate", response_dominant_language["Languages"][0]["LanguageCode"], intent)
            intent = lex.set_slot("text",text, intent)
            print("Intent: ",intent)
            
            return lex.elicit_slot(
                active_contexts, session_attributes, intent,slotToElicit,[{'contentType': 'PlainText', 'content': response_chat}])
           
            
        elif language is not None :
            try: 
                
                targetLanguage = language_en[text_to_translate.lower()]
                response = client_translate.translate_text( Text=text['value']["interpretedValue"], SourceLanguageCode=trasnlate['value']["interpretedValue"], TargetLanguageCode=targetLanguage)
                text_done = response['TranslatedText']
    
    
                response_chat = f" Here yo response: {text_done}".format(text_done)
                
                print(response_chat)
                
                languageCode = to_polly_language[targetLanguage] 
                targetVoice = to_polly_voice[targetLanguage]
                
                response_polly = client_polly.start_speech_synthesis_task(
                                Engine='standard',
                                LanguageCode = languageCode,
                                OutputFormat='mp3',
                                OutputS3BucketName=bucket_name,
                                OutputS3KeyPrefix=bueket_key,
                                Text=text_done,
                                VoiceId= targetVoice
                                )
                print(response_polly)
                
                s3_path = bueket_key + response_polly['SynthesisTask']['OutputUri'].split("/")[-1]  
    
                mp3_presigned_url = utils.generate_presigned_url(bucket_name, s3_path, expiration=3600)
                
                url_short = utils.getShortUrl(mp3_presigned_url)
                
                response_chat = f"Translation result: {text_done} \n \n \n \n Here you can hear the pronunciation: {url_short}".format(text_done,url_short)
                
                print(response_chat)
           
                
                return lex.elicit_intent(
                    active_contexts, session_attributes, intent,[{'contentType': 'PlainText', 'content': response_chat}])
                    
            except:
                response_chat = f" I don't recognize {text_to_translate} as a language, try a valid language (spanish, portuguese, italian, french, english) ".format(text_to_translate)
                return lex.elicit_intent(
                    active_contexts, session_attributes, intent,[{'contentType': 'PlainText', 'content': response_chat}])
            
        else:
            response_chat = f" Wrong value.. try again"
        
            return lex.elicit_intent(
                    active_contexts, session_attributes, intent,[{'contentType': 'PlainText', 'content': response_chat}])


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch sessionId={}, intentName={}'.format(intent_request['sessionId'], intent_request['sessionState']["intent"]['name']))

    interpretations = intent_request['interpretations']
    intent_name = interpretations[0]['intent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'NewIntent':
        return smart_kendra(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    print("evento: ",event)
    
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
    