import os
from pathlib import Path
import re


from botocore.exceptions import ClientError
import boto3
from loguru import logger


def upload_to_r2(title, bucket='podcast'):
    s3 = boto3.resource(
        's3',
        endpoint_url = get_env_var('R2_ENDPOINT_URL'),
        aws_access_key_id = get_env_var('R2_ACCESS_KEY_ID'),
        aws_secret_access_key = get_env_var('R2_SECRET_ACCESS_KEY'),
    )

    filetypes = '(.+\.mp3|index.rss)' #regex pattern in string
    files = collect_files(filetypes)
    podcastbucket = get_or_create_bucket(bucket, s3)
    upload(title, files, podcastbucket)

def get_env_var(name):
    try:
        envvar = os.environ[name]
        return envvar
    except KeyError:
        raise KeyError(f'{name} not set.')

def get_or_create_bucket(bucket, s3):
    podcastbucket = s3.Bucket(bucket)
    if not bucket_exists(podcastbucket, s3):
        podcastbucket.create()
    return podcastbucket

def collect_files(pattern):
    files = [
        p for p in Path('.').glob('*')
        if re.search(pattern, str(p))
    ]
    if not len(files):
        raise FileNotFoundError('required files not found.')
    return files

def upload(title, upload_files, podcastbucket):
    for file in upload_files:
        try:
            podcastbucket.upload_file(file, f'{title}/{file}')
        except ClientError as e:
            logger.error(e)

def bucket_exists(s3bucket, s3) -> bool:
    return s3bucket in s3.buckets.all()
