from pathlib import Path


from podgen import Podcast, Episode, Media


class FeedGenerator:
    def __init__(self):
        pass

    def generate_rss(self, title, hostname):
        podcast = Podcast(
            name=title,
            website=f"https://{hostname}/{title}/",
            description=title,
            explicit=False,
            withhold_from_itunes=True,
        )

        self._add_episodes(title, hostname, podcast)
        podcast.rss_file("index.rss")

    def _add_episodes(self, title, hostname, podcast):
        files = Path(".").glob("*.mp3")
        for file in files:
            media = Media(
                url=f"https://{hostname}/{title}/{file.name}",
                size=file.stat().st_size,
            )
            media.populate_duration_from(file)

            podcast.add_episode(
                Episode(
                    title=file.name,  # filename
                    media=media,
                )
            )
