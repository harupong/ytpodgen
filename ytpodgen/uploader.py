import os
from pathlib import Path
import re


from botocore.exceptions import ClientError
import boto3
from loguru import logger


class Uploader:
    def __init__(self):
        pass

    def upload_to_r2(self, title, bucket="podcast"):
        s3 = boto3.resource(
            "s3",
            endpoint_url=self.get_env_var("R2_ENDPOINT_URL"),
            aws_access_key_id=self.get_env_var("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=self.get_env_var("R2_SECRET_ACCESS_KEY"),
        )

        filetypes = r"(.+\.mp3|index.rss)"  # regex pattern in string
        files = self.collect_files(filetypes)
        podcastbucket = self.get_or_create_bucket(bucket, s3)
        self.upload(title, files, podcastbucket)

    def get_env_var(self, name):
        try:
            envvar = os.environ[name]
            return envvar
        except KeyError:
            raise KeyError(f"{name} not set.")

    def get_or_create_bucket(self, bucket, s3):
        podcastbucket = s3.Bucket(bucket)
        if not self.bucket_exists(podcastbucket, s3):
            podcastbucket.create()
        return podcastbucket

    def collect_files(self, pattern):
        files = [p for p in Path(".").glob("*") if re.search(pattern, str(p))]
        if not len(files):
            raise FileNotFoundError("required files not found.")
        return files

    def upload(self, title, upload_files, podcastbucket):
        for file in upload_files:
            try:
                podcastbucket.upload_file(file, f"{title}/{file}")
            except ClientError as e:
                logger.error(e)

    def bucket_exists(self, s3bucket, s3) -> bool:
        return s3bucket in s3.buckets.all()
