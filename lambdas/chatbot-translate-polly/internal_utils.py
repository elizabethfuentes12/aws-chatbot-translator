import boto3
import os
import time
import logging
import json

import requests

from botocore.exceptions import ClientError


def create_presigned_url(bucket_name, object_name, expiration=3600):

    """Generate a presigned URL to share an S3 object
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def getShortUrl(website):
    shortUrl=requests.get("http://tinyurl.com/api-create.php?url="+website);
    return shortUrl.content.decode("utf-8")
