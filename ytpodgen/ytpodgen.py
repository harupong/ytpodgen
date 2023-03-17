import os
from importlib.metadata import version
from textwrap import dedent


import click
from loguru import logger
import requests


from . import downloader
from . import feedgenerator
from . import uploader

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    ytpodgen_version = version('ytpodgen')
    click.echo(ytpodgen_version)
    ctx.exit()

def send_slack_notification(message):
    data = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=data)

@click.command()
@click.option('--title', prompt='enter title', help='title for the podcast')
@click.option(
    '--hostname',
    prompt='enter hostname',
    help='hostname(custom or r2.dev) to serve files'
)
@click.option(
    '--liveurl',
    help='watch for and download the specified YouTube Live URL'
)
@click.option(
    '--upload-r2',
    is_flag=True,
    help='if specified, upload mp3s/RSS to Cloudflare R2'
)
@click.option('--debug', is_flag=True, help='run yt-dlp in debug mode')
@click.option(
    '--version',
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True
)
def cli(title, hostname, liveurl, upload_r2, debug):
    logger.add(
        f"{title}.log",
        level="INFO"
    )
    if SLACK_WEBHOOK_URL:
        logger.add(
            send_slack_notification,
            level="SUCCESS"
        )

    try:
        while True:
            if liveurl:
                logger.info("Running yt-dlp...")
                downloader.download(title, liveurl)

            logger.info("Generating feeds...")
            feedgenerator.generate_rss(title, hostname)

            if upload_r2:
                logger.info("Uploading files...")
                uploader.upload_to_r2(title)
                logger.success(
                    dedent(
                        f"""
                        Upload completed.
                        Podcast feed url: https://{hostname}/{title}/index.rss
                        """
                    ).strip("\n")
                )
            
            if liveurl is None:
                break
    except Exception as e:
        logger.error(f"ytpodgen failed with following error messages: {e}")

if __name__ == '__main__':
    cli()
