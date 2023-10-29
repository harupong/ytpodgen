import os
from pathlib import Path
import re


from botocore.exceptions import ClientError
import boto3
from loguru import logger


class Uploader:
    def __init__(self):
        pass

    @staticmethod
    def upload_to_r2(path, bucket="podcast"):
        s3 = boto3.resource(
            "s3",
            endpoint_url=Uploader.get_env_var("R2_ENDPOINT_URL"),
            aws_access_key_id=Uploader.get_env_var("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=Uploader.get_env_var("R2_SECRET_ACCESS_KEY"),
            region_name="auto"
        )

        filetypes = r"(.+\.mp3|index.rss)"  # regex pattern in string
        files = Uploader.collect_files(filetypes)
        podcastbucket = Uploader.get_or_create_bucket(bucket, s3)
        Uploader.upload(path, files, podcastbucket)

    @staticmethod
    def get_env_var(name):
        try:
            envvar = os.environ[name]
            return envvar
        except KeyError:
            raise KeyError(f"{name} not set.")

    @staticmethod
    def get_or_create_bucket(bucket, s3):
        podcastbucket = s3.Bucket(bucket)
        if not Uploader.bucket_exists(podcastbucket, s3):
            podcastbucket.create()
        return podcastbucket

    @staticmethod
    def collect_files(pattern):
        files = [p for p in Path(".").glob("*") if re.search(pattern, str(p))]
        if not len(files):
            raise FileNotFoundError("required files not found.")
        return files

    @staticmethod
    def upload(path, upload_files, podcastbucket):
        for file in upload_files:
            try:
                podcastbucket.upload_file(file, f"{path}/{file}")
            except ClientError as e:
                logger.error(e)

    @staticmethod
    def bucket_exists(s3bucket, s3) -> bool:
        return s3bucket in s3.buckets.all()
