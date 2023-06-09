import lex_utils as dialog
from datetime import datetime, timedelta
import locale
import boto3
import time

client_translate = boto3.client('translate')
client_polly = boto3.client('polly')

language_en = dict( [ ('spanish', 'es'), ('portuguese', 'pt-PT'), ('italian', 'it'), ('french', 'fr'),('english', 'en') ] )
to_polly_voice = dict( [ ('en', 'Amy'), ('es', 'Conchita'), ('fr', 'Chantal'), ('pt-PT', 'Cristiano'),('it', 'Giorgio') ] )
to_polly_language = dict( [ ('en', 'en-US'), ('es', 'es-US'), ('fr', 'fr-FR'), ('pt-PT' , 'pt-BR'),('it', 'it-IT') ] )

bucket_name = "demo-eli"
bueket_key = "traductor_polly/"

client_translate = boto3.client('translate')
client_polly = boto3.client('polly')

def to_translate(text,sourceLanguage,targetLanguage):
    text_done = client_translate.translate_text( Text=text, SourceLanguageCode=sourceLanguage, TargetLanguageCode=targetLanguage)
    
    if text_done["ResponseMetadata"]['HTTPStatusCode'] == 200:
        print("Text translated")
        text_done = text_done['TranslatedText']
    else: 
        print("error")
        text_done = "Hubo un error, intenta nuevamente"
    print("text_done", text_done)
    return text_done

def to_polly (text_done,bueket_key,bucket_name,languageCode,targetVoice):
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
    
    if response_polly['ResponseMetadata']['HTTPStatusCode'] == 200:
        print("Text polly in progress")
        max_time = time.time() + 2 # 3 hours
        while time.time() < max_time:
            response_task = client_polly.get_speech_synthesis_task(
                            TaskId=response_polly['SynthesisTask']['TaskId']
                            )
            status = response_task['SynthesisTask']['TaskStatus']
            print("Polly SynthesisTask: {}".format(status))
            if status == "completed" or status == "failed":
                break
            time.sleep(2)
        text_done = response_polly['SynthesisTask']['OutputUri']
    else: 
        print("error")
        text_done = "Upps, try again"
    return text_done
    
def generate_presigned_url(s3_bucket, s3_path, expiration=3600):
    """
    Generate a pre-signed URL for an S3 object.
    """
    # Create an S3 client
    s3_client = boto3.client('s3')
    # Generate the pre-signed URL
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': s3_bucket, 'Key': s3_path},
        ExpiresIn=expiration
    )
    return presigned_url
    
def process_intent (text, language_in, lenguage_out):
    
    sourceLanguage = language_en[language_in] 
    targetLanguage = language_en[lenguage_out]       
    text_done = to_translate(text,sourceLanguage,targetLanguage)
    languageCode = to_polly_language[targetLanguage] 
    targetVoice = to_polly_voice[targetLanguage] 
    polly_response = to_polly(text_done,bueket_key,bucket_name,languageCode,targetVoice)   
    s3_path = bueket_key + polly_response.split("/")[-1]  

    mp3_presigned_url = generate_presigned_url(bucket_name, s3_path, expiration=3600)
    response_chat = f"Resultado de la traducción: {text_done} \n \n Aca puedes oir la pronunciación: {mp3_presigned_url}".format(text_done,mp3_presigned_url)

    return response_chat
    


def translate(intent_request, messages):
    content_type =  'PlainText'
    intent = dialog.get_intent(intent_request)
    active_contexts = dialog.get_active_contexts(intent_request)
    session_attributes = dialog.get_session_attributes(intent_request)
    
    print ("slotToElicit: ",intent_request["proposedNextState"]["dialogAction"]["slotToElicit"])
    
    if intent['state'] == 'ReadyForFulfillment':
        
        lenguage_out = dialog.get_slot('Idioma', intent).lower()
        text = dialog.get_slot('Texto', intent)
        language_in = dialog.get_slot('LanguajeIn', intent).lower()
        print ('LanguageOut:', lenguage_out)
        print ('Texto:', text)
        print ('LanguageIn:', language_in)  
        response_chat = process_intent(text, language_in, lenguage_out)
        return dialog.elicit_intent(
                active_contexts, session_attributes, intent, 
                [{'contentType': 'PlainText', 'content': response_chat}])
                
    elif intent['state'] == 'InProgress' and intent_request["proposedNextState"]["dialogAction"]["slotToElicit"] == "Texto" and intent_request["proposedNextState"]["prompt"]["attempt"] == "Retry1":
        print('InProgress')
        if dialog.get_slot('Texto', intent) is None: 
            text = intent_request["inputTranscript"]
            lenguage_out = dialog.get_slot('Idioma', intent).lower()
            language_in = dialog.get_slot('LanguajeIn', intent).lower()
            print ('LanguageOut:', lenguage_out)
            print ('Texto:', text)
            print ('LanguageIn:', language_in)  

            response_chat = process_intent(text, language_in, lenguage_out)

            return dialog.elicit_intent(
                    active_contexts, session_attributes, intent, 
                    [{'contentType': 'PlainText', 'content': response_chat}])
    else:
        return dialog.delegate(active_contexts, session_attributes, intent)
