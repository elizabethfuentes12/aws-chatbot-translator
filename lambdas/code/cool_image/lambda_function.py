import json
import lex_utils as lex_lib
import boto3
import os
import base64
import lambda_utils as lambda_utils
from io import BytesIO
import base64
from PIL import Image as OpenImage
import time
import numpy as np

ENDPOINT_TEXT_TO_TEXT = os.environ.get('ENV_ENDPOINT_TEXT_TO_TEXT')
ENDPOINT_TEXT_TO_IMAGE = os.environ.get('ENV_ENDPOINT_TEXT_TO_IMAGE')
REGION_ENDPOINT = os.environ.get('ENV_REGION_ENDPOINT')
bucket_name = os.environ.get('ENV_BUCKET_NAME')
distribution_name = os.environ.get('ENV_DISTRIBUTION_NAME')

client_translate = boto3.client('translate')

# Create an S3 client
s3_client = boto3.client('s3')

runtime = boto3.Session().client('sagemaker-runtime',region_name=REGION_ENDPOINT)

#Function to process response of endopoints 

def parse_response_multiple_texts(query_response):
    model_predictions = json.loads(query_response["Body"].read())
    print("model_predictions: ",model_predictions)
    generated_text = model_predictions["generated_texts"]
    return generated_text
    
def query_endpoint_with_json_payload(encoded_json, endpoint_name):
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name, ContentType="application/json", Body=encoded_json
    )
    return response
    

#https://github.com/aws-samples/aws-lex-web-ui 
    
#https://aws.amazon.com/marketplace/ai/procurement?productId=96e6989b-7f37-4637-8fd6-e775787405bd
#https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpoint.html
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime.html

def fun_text_to_image(ENDPOINT_TEXT_TO_IMAGE,text):
    """
        Styles
        ["enhance", "anime", "photographic", "digital-art", "comic-book", "fantasy-art", "line-art", "analog-film", 
                        "neon-punk", "isometric", "low-poly", "origami", "modeling-compound", "cinematic",
                        "3d-model", "pixel-art", "tile-texture"]
        """
    payload = {
    "prompt": text,
    "width": 512,
    "height": 512,
    "num_images_per_prompt": 1,
    "num_inference_steps": 50,
    "guidance_scale": 7.5,
    "seed": 1,
    }

    encoded_payload = json.dumps(payload).encode("utf-8")
    query_response = runtime.invoke_endpoint(EndpointName=ENDPOINT_TEXT_TO_IMAGE,
                                        ContentType='application/json',
                                        Accept="application/json",
                                        Body=encoded_payload)
    print(query_response)
    response_dict = json.loads(query_response['Body'].read())

    x = np.asarray(response_dict['generated_images'][0], dtype=np.uint8)
    
    #Save Image
    file_name = time.strftime("%Y%m%d-%H%M%S") +'.png'
    OpenImage.fromarray(x).save('/tmp/' + file_name)
            
    s3 = boto3.client("s3")

    bucket_folder = "text_to_image/"
    
    s3_path = bucket_folder  + file_name
    s3.upload_file('/tmp/' + file_name, bucket_name, s3_path, ExtraArgs={'Metadata': {'prompt': text}})

    s3_url = distribution_name+"/"+s3_path

    return s3_url

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
    print("sesion atr",session_attributes)
    previous_slot_to_elicit = session_attributes.get("slot_to_elicit") #to find out when amazon lex is asking for text_to_translate and join the conversation.
    attempt = event["proposedNextState"]["prompt"]["attempt"]
    print("attempt",attempt)
    
    print("previous_slot_to_elicit",previous_slot_to_elicit)

    if intent_name == 'text_to_image':
        print("intent_name",intent_name)

        text_explain = event["inputTranscript"]
        print("text_to_image",text_explain)

        if (text_explain != None) and (attempt=="Retry1"): 
            
            translated_text, dominant_language = lambda_utils.translate_to_en(text_explain)
            
            text = event["inputTranscript"]
            print("translated_text",translated_text)
            print(ENDPOINT_TEXT_TO_IMAGE)
            s3_url = fun_text_to_image(ENDPOINT_TEXT_TO_IMAGE,translated_text)
            text_1 = lambda_utils.translate_from_english("Titulo: ", dominant_language)

            text_2 = lambda_utils.translate_from_english("Do you want to try again? Write: ", dominant_language)

            response = f"<img src='https://{s3_url}'/img> {text_1} {text_explain} </br> </br> {text_2} cool image"
            messages =  [{'contentType': 'CustomPayload', 'content': response}]

            #print(lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages))
            #return lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages)
            print(lex_lib.close(active_contexts, session_attributes, intent, messages))
            return lex_lib.close(active_contexts, session_attributes, intent, messages)

