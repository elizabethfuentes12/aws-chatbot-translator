import json
import lex_utils as lex_lib
import boto3
import utils
import os
import time

client_translate = boto3.client('translate')

bucket_name = os.environ.get('ENV_BUCKET_NAME')
distribution_name = os.environ.get('ENV_DISTRIBUTION_NAME')
bucket_folder = "traductor_polly/"

def translate_text (text,language_out):
    response = client_translate.translate_text(
    Text=text,
    SourceLanguageCode="auto",
    TargetLanguageCode=language_out  
)
    return response['TranslatedText'] 


def text_to_speech(text,language_out):
    polly_client = boto3.client('polly')
    to_polly_voice = dict( [ ('en', 'Amy'), ('es', 'Conchita'), ('fr', 'Chantal'), ('pt-PT', 'Cristiano'),('it', 'Giorgio'),("sr","Carmen"),("zh","Hiujin") ] )
    to_polly_language = dict( [ ('en', 'en-US'), ('es', 'es-US'), ('fr', 'fr-FR'), ('pt-PT' , 'pt-BR'),('it', 'it-IT'),("sr","ro-RO"),("zh","Yue-CN") ] )
    languageCode = to_polly_language[language_out] 
    targetVoice = to_polly_voice[language_out]

    response = polly_client.start_speech_synthesis_task(
        OutputFormat='mp3',
        Text=text,
        VoiceId=targetVoice,
        LanguageCode = languageCode,
        OutputS3BucketName=bucket_name ,
        OutputS3KeyPrefix=bucket_key,
    )
    
    print(response)
    s3 = boto3.client("s3")

    file_name = response['SynthesisTask']['OutputUri'].split("/")[-1] 
    
    s3_path = bucket_folder + file_name
    
    s3.upload_file('/tmp/' + file_name, bucket_name, s3_path, ExtraArgs={'Metadata': {'prompt': text}})

    s3_url = distribution_name+"/"+s3_path

    
    return url_short


def lambda_handler(event, context):
    # TODO implement
    print(event)

    #Lambda Function Input Event and Response Format
    #https://docs.aws.amazon.com/lex/latest/dg/lambda-input-response-format.html
    
    interpretations = event['interpretations']
    intent_name = interpretations[0]['intent']['name']
    intent = lex_lib.get_intent(event)
    #need it to Response Format
    active_contexts = lex_lib.get_active_contexts(event) 
    session_attributes = lex_lib.get_session_attributes(event) 
    previous_slot_to_elicit = session_attributes.get("previous_slot_to_elicit") #to find out when amazon lex is asking for text_to_translate and join the conversation.
    
    if intent_name == 'TranslateIntent':
        print(intent_name)
        language_out = lex_lib.get_slot("language_out",intent)
        text_to_translate = lex_lib.get_slot("text_to_translate",intent)
        yes_no = lex_lib.get_slot("yes-no",intent)
        print(language_out,yes_no)

        if language_out == None:
            return lex_lib.delegate(active_contexts, session_attributes, intent)
            
        if (text_to_translate == None) and (language_out != None) and (previous_slot_to_elicit != "text_to_translate") and (session_attributes.get('url_short') == None):
            response = "What text do you want to translate?"
            messages =  [{'contentType': 'PlainText', 'content': response}]
            print(lex_lib.elicit_slot("text_to_translate", active_contexts, session_attributes, intent, messages))
            return lex_lib.elicit_slot("text_to_translate", active_contexts, session_attributes, intent, messages)
     
        
        if  (previous_slot_to_elicit == "text_to_translate") and (language_out != None) and (session_attributes.get('url_short') == None): 
            print("diferente a none")
            text_to_translate = event["inputTranscript"]
            text_ready = translate_text(text_to_translate,language_out)
            
            session_attributes['url_short'] = text_to_speech(text_ready,language_out)
            print ("url_short: ", session_attributes['url_short'])
           
            
            response = f"The translate text is: {text_ready}. Would you like to hear the pronunciation? (yes/no)"
            messages =  [{'contentType': 'PlainText', 'content': response}]
            
            print(lex_lib.confirm_intent(active_contexts, session_attributes, intent, messages))
            return lex_lib.confirm_intent(active_contexts, session_attributes, intent, messages)
        
            
        if intent['confirmationState'] == 'Confirmed': 
            url_short = session_attributes.get('url_short')
            time.sleep(3)
            response = f" Hear the pronunciation here {url_short}"
            messages =  [{'contentType': 'PlainText', 'content': response}]
                
            print(lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages))
            return lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages)
            
        if intent['confirmationState'] == 'Denied':
                
            response = f"Have a nice day"
            messages =  [{'contentType': 'PlainText', 'content': response}]
                
            print(lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages))
            return lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages)
                
    
       
        
        