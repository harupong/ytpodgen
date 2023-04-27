import argparse
import os
import hashlib
from importlib.metadata import version
from pathlib import Path
import re
from textwrap import dedent


from loguru import logger
import requests


from ytpodgen.downloader import Downloader
from ytpodgen.feedgenerator import FeedGenerator
from ytpodgen.uploader import Uploader


SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")


def send_slack_notification(message):
    data = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=data)


def get_version():
    return version("ytpodgen")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Podcast generator")
    parser.add_argument(
        "--title",
        required=True,
        help="title for the podcast"
    )
    parser.add_argument(
        "--hostname",
        required=True,
        help="hostname(custom or r2.dev) to serve files"
    )
    parser.add_argument(
        "--liveurl",
        type=validate_url,
        help="Watch for and download the specified YouTube Live URL."
    )
    parser.add_argument(
        "--upload-r2",
        action="store_true",
        help="If specified, upload mp3s/RSS to Cloudflare R2.",
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory(default: current directory)"
    )
    parser.add_argument(
        "--bucket",
        default="podcast",
        help="R2 Bucket name to upload files(default: podcast)"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="If specified, make the podcast private by generating hashed url."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=get_version(),
        help="Show version and exit.",
    )

    args = parser.parse_args()
    return args


def validate_url(url):
    if re.match(r"^https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})", url):
        return url
    if not url.startswith("https://www.youtube.com/"):
        raise argparse.ArgumentTypeError(
            f"""
            Invalid url {url}.
            It must be a YouTube Live URL that starts with https://www.youtube.com/.
            """
        )
    if not url.endswith("/live"):
        raise argparse.ArgumentTypeError(
            f"""
            Invalid url {url}.
            It must be a YouTube Live URL that ends with /live.
            """
        )
    return url


def main():
    args = parse_arguments()

    change_work_dir(args.output, args.title)
    create_logger(args.title)

    try:
        while True:
            run(args)
            if args.liveurl is None:
                break
    except Exception as e:
        logger.error(f"ytpodgen failed with following error messages: {e}")


def create_logger(title):
    logger.add(f"{title}.log", level="INFO")
    if SLACK_WEBHOOK_URL:
        logger.add(send_slack_notification, level="SUCCESS")


def change_work_dir(output, title):
    try:
        work_dir = Path.cwd()
        if output:
            work_dir = Path(output).absolute()
        os.chdir(work_dir)
    except FileNotFoundError:
        create_logger(title)
        logger.error(f"Invalid argument {output} for --output option.")
        exit()


def run(args):
    path = generate_hashed_path(args.title) if args.private else args.title

    if args.liveurl:
        logger.info("Running yt-dlp...")
        Downloader.download(args.title, args.liveurl)

    logger.info("Generating feeds...")
    FeedGenerator.generate_rss(args.title, args.hostname, path)

    if args.upload_r2:
        logger.info("Uploading files...")
        Uploader.upload_to_r2(path, args.bucket)
        logger.success(
            dedent(
                f"""
            {args.title} Uploaded.
            Podcast feed url: https://{args.hostname}/{path}/index.rss
            """
            ).strip("\n")
        )


def generate_hashed_path(title):
    hashed_path = hashlib.sha256(title.encode("utf-8")).hexdigest()
    return hashed_path


if __name__ == "__main__":
    main()
