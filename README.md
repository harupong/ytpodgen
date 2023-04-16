# ytpodgen - turns YouTube live streams into podcasts
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## prerequisite
- python3 and pip

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

## examples
### wait for new livestream, and once on the air, record it and generate podcast RSS in background
```
TITLE=<title> ; #title for your podcast
LIVEURL=<liveurl> ; #YouTube live URL that ends with "/live"
HOSTNAME=<hostname> ; #hostname to serve files from
screen -dmS ${TITLE} ytpodgen --liveurl ${LIVEURL} --title ${TITLE} --hostname ${HOSTNAME}
```

When completed, `ytpodgen` will wait for another livestream. Since all the waiting might take a while, I prefer running this in background using `screen`.

### Why not upload them as well!?
You can pass `--upload-r2` argument to enable file uploadig to Cloudflare R2. By enabling it, mp3s/RSS are uploaded to Cloudflare R2.

For example, by running the commands below , you create a screen session that waits for YouTube livestream on the given URL and saves the data under current directory if there is a livestream.

```
TITLE=<title> ; #title for your podcast
LIVEURL=<liveurl> ; #YouTube live URL that ends with "/live"
HOSTNAME=<hostname> ; #hostname to serve files from
screen -dmS ${TITLE} ytpodgen --upload-r2 --liveurl ${LIVEURL} --title ${TITLE} --hostname ${HOSTNAME}
```

### I just want to generate RSS from mp3 files, no download/upload needed
```
TITLE=<title> ; #title for your podcast
HOSTNAME=<hostname> ; #hostname to serve files from
ytpodgen --title ${TITLE} --hostname ${HOSTNAME}
```

This generates `index.rss` file under current directory and exits.

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
