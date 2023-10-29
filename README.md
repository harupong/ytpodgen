# ytpodgen
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Command line tool to turn YouTube live streams into podcasts. It watches out for new YouTube live streams, and once on the air, records the livestream, converts it to audio file, generates podcast RSS, and uploads them to Cloudflare R2.

## prerequisite
- python3 and pip

Tested only on Mac and Linux.

## first time setup
```
python3 -m pip install --user ytpodgen
```

Set environment variable `SLACK_WEBHOOK_URL`, if you want Slack notification.

If you want to upload files to Cloudflare R2 as well, don't forget to set three environment variables for Cloudflare R2. 

- R2_ENDPOINT_URL
- R2_ACCESS_KEY_ID
- R2_SECRET_ACCESS_KEY

For now, R2 bucket name must be `podcast`.

## usage
```
usage: ytpodgen [-h] --title TITLE --hostname HOSTNAME [--liveurl LIVEURL] [--upload-r2] [--output OUTPUT] [--bucket BUCKET] [--private] [--version]

Podcast generator

options:
  -h, --help           show this help message and exit
  --title TITLE        title for the podcast
  --hostname HOSTNAME  hostname(custom or r2.dev) to serve files
  --liveurl LIVEURL    Watch for and download the specified YouTube Live URL.
  --upload-r2          If specified, upload mp3s/RSS to Cloudflare R2.
  --output OUTPUT      Output directory(default: current directory)
  --bucket BUCKET      R2 Bucket name to upload files(default: podcast)
  --private            If specified, make the podcast private by generating hashed url.
  --version            Show version and exit.
```

## examples
### MY USE CASE: wait for new livestream in background, and once on the air, record it, generate podcast RSS, and upload them to Cloudflare R2
```
screen -dmS <TITLE> ytpodgen --liveurl <LIVEURL> --title <TITLE> --hostname <HOSTNAME> --upload-r2
```

When completed, `ytpodgen` will wait for another livestream. Since all the waiting might take a while, I prefer running this in background using `screen`.

### a few options you might wanna take a look at
#### private
When you want to make a podcast private, using basic auth to restrict access is the best way to go. However, it requires additional setup, and some podcast apps don't support basic auth.

By passing this option, you can generate hashed url for the podcast. It is far less secure than basic auth, but it is easier to setup, and it works with most podcast apps.

I'm using this option to sync audiobook files to the podcast app on my Garmin smartwatch. 
#### bucket BUCKET
By default, `ytpodgen` uploads files to `podcast` bucket. If you want to upload files to a different bucket, you can specify it with this option.

I'm using this option to switch between a bucket that is password protected by basic auth, and a bucket that is not.  Be careful what to pass to the `--hostname` option when you use this option, as the hostname must match the bucket name.

### I just want to generate RSS from mp3 files, no download/upload needed
```
ytpodgen --title <TITLE> --hostname <HOSTNAME>
```

This generates `index.rss` file from the mp3 files in current directory and exits.

## How to release
Executing the commands below, and the GitHub Actions publishes new package to PyPI.

```bash
poetry version <patch/minor/major>
git add pyproject.toml && git commit -m $(poetry version -s)
git push origin main
gh release create --generate-notes "v$(poetry version -s)"
git fetch --tags origin
```

## Why only Cloudflare R2, and not other S3-compatible cloud storage?
Because:

- It offers free tier for up to 10GB of storage space per month
- With Cloudflare Worker, basic auth can be applied to the uploaded files that are made public

## how I configured basic auth on Cloudflare R2 using Cloudflare Workers
1. connected a custom domain to my R2 bucket, to make the bucket public. [docs](https://developers.cloudflare.com/r2/buckets/public-buckets/)
2. configured a basic auth worker by following steps described [here](https://qiita.com/AnaKutsu/items/1c8bd0eb938edd3c0e0a).
3. replaced the plaintext declaration of password with worker env var. [docs](https://developers.cloudflare.com/workers/platform/environment-variables/#environment-variables-via-the-dashboard)
4. added a trigger(custom domain route) to the basic auth worker. [docs](https://developers.cloudflare.com/workers/platform/triggers/routes/)

## TODO/IDEAS
moved to [GitHub issues](https://github.com/harupong/ytpodgen/issues/)
