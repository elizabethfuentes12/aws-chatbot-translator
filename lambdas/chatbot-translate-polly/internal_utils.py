import boto3
import os
import time
import logging
import json

import requests

def generate_presigned_url(s3_bucket, s3_path, expiration=3600):
    """
    Generate a pre-signed URL for an S3 object.
    """
    s3_client = boto3.client('s3')

    # Generate the pre-signed URL
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': s3_bucket, 'Key': s3_path},
        ExpiresIn=expiration
    )
    return presigned_url

def getShortUrl(website):
    shortUrl=requests.get("http://tinyurl.com/api-create.php?url="+website);
    return shortUrl.content.decode("utf-8")
