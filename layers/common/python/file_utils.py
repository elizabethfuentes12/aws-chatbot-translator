import boto3
import requests

s3_resource = boto3.resource('s3')


def upload_data_to_s3(bytes_data,bucket_name, s3_key):
    obj = s3_resource.Object(bucket_name, s3_key)
    obj.put(ACL='private', Body=bytes_data)
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    return s3_url

def download_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None

def get_media_url(mediaId,whatsToken):
    
    URL = 'https://graph.facebook.com/v17.0/'+mediaId
    headers = {'Authorization':  whatsToken}
    print("Requesting")
    response = requests.get(URL, headers=headers)
    responsejson = response.json()
    if('url' in responsejson):
        print("Responses: "+ str(responsejson))
        return responsejson['url']
    else:
        print("No URL returned")
        return None

def get_whats_media(url,whatsToken):
    headers = {'Authorization':  whatsToken}
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        return None