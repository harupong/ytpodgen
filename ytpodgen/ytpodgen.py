import os
from importlib.metadata import version
from pathlib import Path
from textwrap import dedent


import click
from loguru import logger
import requests


from ytpodgen import downloader, feedgenerator, uploader

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

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
    help='Watch for and download the specified YouTube Live URL.'
)
@click.option(
    '--upload-r2',
    is_flag=True,
    help='If specified, upload mp3s/RSS to Cloudflare R2.'
)
@click.option(
    '--output',
    help='Output directory(default: current directory)'
)
@click.option(
    '--version',
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help='Show version and exit.'
)

def cli(title, hostname, liveurl, upload_r2, output):
    change_work_dir(output, title)
    create_logger(title)

    try:
        while True:
            run(title, hostname, liveurl, upload_r2)
            if liveurl is None:
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

def run(title, hostname, liveurl, upload_r2):
    if liveurl:
        logger.info("Running yt-dlp...")
        downloader.download(title, liveurl)

    logger.info("Generating feeds...")
    feedgenerator.generate_rss(title, hostname)

    if upload_r2:
        logger.info("Uploading files...")
        uploader.upload_to_r2(title)
        logger.success(dedent(
            f"""
            Upload completed.  Podcast feed url:
            https://{hostname}/{title}/index.rss
            """
            ).strip("\n")
        )

if __name__ == '__main__':
    cli()
