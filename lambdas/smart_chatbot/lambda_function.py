import json
import lex_utils as lex_lib
import boto3
import os
import base64
import lambda_utils as lambda_utils
from io import BytesIO
import base64
from PIL import Image as OpenImage
import random
import time

ENDPOINT_TEXT_TO_TEXT = os.environ.get('ENV_ENDPOINT_TEXT_TO_TEXT')
ENDPOINT_TEXT_TO_IMAGE = os.environ.get('ENV_ENDPOINT_TEXT_TO_IMAGE')
REGION_ENDPOINT = os.environ.get('ENV_REGION_ENDPOINT')


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
    

#https://github.com/aws/amazon-sagemaker-examples/blob/main/introduction_to_amazon_algorithms/jumpstart_text_summarization/Amazon_JumpStart_Text_Summarization.ipynb

def summarize(ENDPOINT_TEXT_TO_TEXT,text_response):
    num_return_sequences = 3
    parameters = {
        "max_length": 50,
        "max_time": 50,
        "num_return_sequences": num_return_sequences,
        "top_k": 50,
        "top_p": 0.95,
        "do_sample": True,
    }

    promt = "Generate a short summary this sentence:\n{text_response}"
    payload = {"text_inputs": promt.replace("{text_response}", text_response), **parameters}

    query_response = query_endpoint_with_json_payload(
                        json.dumps(payload).encode("utf-8"), endpoint_name=ENDPOINT_TEXT_TO_TEXT)
    generated_texts = parse_response_multiple_texts(query_response)
    print(generated_texts)
    result = generated_texts[0]
    return result

#https://aws.amazon.com/marketplace/ai/procurement?productId=96e6989b-7f37-4637-8fd6-e775787405bd
#https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_runtime_InvokeEndpoint.html
#https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker-runtime.html

def fun_text_to_image(ENDPOINT_TEXT_TO_IMAGE,text,style):
    """
        Styles
        ["enhance", "anime", "photographic", "digital-art", "comic-book", "fantasy-art", "line-art", "analog-film", 
                        "neon-punk", "isometric", "low-poly", "origami", "modeling-compound", "cinematic",
                        "3d-model", "pixel-art", "tile-texture"]
        """

    payload = {
        "text_prompts": [{"text":text}],
        "style_preset": style,
        "seed" : 1234
    }

    encoded_payload = json.dumps(payload).encode("utf-8")
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_TEXT_TO_IMAGE,
    #                                    ContentType='application/x-text',
                                        ContentType='application/json',
                                        Accept="application/json",
    #                                    Accept="image/png",
                                        Body=encoded_payload)
    
    image = json.loads(response['Body'].read())

    if image['result'] == "error":
        
        print(image['error'])
        print(image['error']['message'])
        message = image['error']['message']
        
    else:
        
        image = image['artifacts'][0]['base64']
        image_data = base64.b64decode(image.encode())
        image = OpenImage.open(BytesIO(image_data))

        #Save Image
        file_name = time.strftime("%Y%m%d-%H%M%S") +'.png'
        image.save('/tmp/' + file_name)
        
        s3 = boto3.client("s3")
        bucket_name = os.environ['ENV_BUCKET_NAME']
        #bucket_folder =os.environ['bucket_folder']
        bucket_folder = "text_to_image/"
        s3_path = bucket_folder  + file_name
        s3.upload_file('/tmp/' + file_name, bucket_name, s3_path, ExtraArgs={'Metadata': {'prompt': text}})
        
        #Signed URL
        
        url = boto3.client('s3').generate_presigned_url(
                ClientMethod='get_object', 
                Params={'Bucket': bucket_name , 'Key': s3_path},
                ExpiresIn=180)
    
        s3_url = url
        
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
    previous_slot_to_elicit = session_attributes.get("previous_slot_to_elicit") #to find out when amazon lex is asking for text_to_translate and join the conversation.
    attempt = event["proposedNextState"]["prompt"]["attempt"]
    print(attempt)
    
    print(previous_slot_to_elicit)
    
    if intent_name == 'summarize':
        print(intent_name)
        text_to_summarize = lex_lib.get_slot("text_to_summarize",intent)
        print(text_to_summarize)
        
        if attempt=="Initial":
            print("entra text_to_summarize")
            response = "What text do you want to summarize?"
            messages =  [{'contentType': 'PlainText', 'content': response}]
            print(lex_lib.elicit_slot("text_to_summarize", active_contexts, session_attributes, intent, messages))
            return lex_lib.elicit_slot("text_to_summarize", active_contexts, session_attributes, intent, messages)
       
        if  attempt=="Retry1": 
            print("entra summarize")
            text_to_summarize = event["inputTranscript"]
            text_ready = summarize(ENDPOINT_TEXT_TO_TEXT,text_to_summarize)
            response = f"The summarize text is: {text_ready}."
            messages =  [{'contentType': 'PlainText', 'content': response}]
            print(lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages))
            return lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages)
            
    if intent_name == 'text_to_image':
        print(intent_name)
        style = lex_lib.get_slot("styleimage",intent)
        text_to_image = lex_lib.get_slot("text_explain",intent)
        print(style,text_to_image)
        
        if style == None:
            return lex_lib.delegate(active_contexts, session_attributes, intent)
        
        if (text_to_image == None) and (style != None) and (previous_slot_to_elicit != "text_explain"):
            response = "tell me what image you would like me to create for you"
            messages =  [{'contentType': 'PlainText', 'content': response}]
            print(lex_lib.elicit_slot("text_explain", active_contexts, session_attributes, intent, messages))
            return lex_lib.elicit_slot("text_explain", active_contexts, session_attributes, intent, messages)
       
        if (previous_slot_to_elicit == "text_explain") and (attempt=="Retry1"): 
            
            text = event["inputTranscript"]
            print(text)
            print(ENDPOINT_TEXT_TO_IMAGE)
            print(style)
            s3_url = fun_text_to_image(ENDPOINT_TEXT_TO_IMAGE,text,style)
            
            response = f"You image: {text}, is here {s3_url}"

            messages =  [{'contentType': 'PlainText', 'content': response}]
            
            print(lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages))
            return lex_lib.elicit_intent(active_contexts, session_attributes, intent, messages)
