import datetime
from pathlib import Path


from podgen import Podcast, Episode, Media


class FeedGenerator:
    def __init__(self):
        pass

    @staticmethod
    def generate_rss(title, hostname):
        podcast = Podcast(
            name=title,
            website=f"https://{hostname}/{title}/",
            description=title,
            explicit=False,
            withhold_from_itunes=True,
        )

        FeedGenerator._add_episodes(title, hostname, podcast)
        podcast.rss_file("index.rss")

    @staticmethod
    def _add_episodes(title, hostname, podcast):
        files = Path(".").glob("*.mp3")
        for file in sorted(files, reverse=True):
            media = Media(
                url=f"https://{hostname}/{title}/{file.name}",
                size=file.stat().st_size,
            )
            media.populate_duration_from(file)

            podcast.add_episode(
                Episode(
                    title=file.name,  # filename
                    media=media,
                    publication_date=datetime.datetime.fromtimestamp(
                        file.stat().st_ctime,
                        datetime.timezone.utc,
                    ),
                )
            )
