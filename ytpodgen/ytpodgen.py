import argparse
import os
from importlib.metadata import version
from pathlib import Path
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
        "--version",
        action="version",
        version=get_version(),
        help="Show version and exit.",
    )

    args = parser.parse_args()
    return args


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
    if args.liveurl:
        logger.info("Running yt-dlp...")
        Downloader.download(args.title, args.liveurl)

    logger.info("Generating feeds...")
    FeedGenerator.generate_rss(args.title, args.hostname)

    if args.upload_r2:
        logger.info("Uploading files...")
        Uploader.upload_to_r2(args.title)
        logger.success(
            dedent(
                f"""
            Upload completed.  Podcast feed url:
            https://{args.hostname}/{args.title}/index.rss
            """
            ).strip("\n")
        )


if __name__ == "__main__":
    main()
