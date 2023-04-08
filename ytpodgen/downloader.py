from yt_dlp import YoutubeDL


class Downloader:
    def __init__(self):
        pass

    @staticmethod
    def download(title, liveurl):
        live_from_start = True if Downloader._is_live(liveurl) else False

        # See help(yt_dlp.YoutubeDL) for a list of available options
        # and public functions
        # https://github.com/yt-dlp/yt-dlp/blob/216bcb66d7dce0762767d751dad10650cb57da9d/yt_dlp/YoutubeDL.py#L184
        ydl_opts = {
            # best audio-only format if available,
            # and if not, fall back to best format that contains both video and audio
            "format": "bestaudio/best",
            "wait_for_video": (60, 60),
            "outtmpl": f"{title}_%(epoch>%Y%m%d%H%M%S)s_%(id)s",
            "live_from_start": live_from_start,
            "postprocessors": [
                {  # Extract audio using ffmpeg
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "64",
                }
            ],
            "postprocessor_args": [
                "-ac",
                "1",  # audio channel mono
            ],
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(liveurl)

    @staticmethod
    def _is_live(liveurl):
        ydl_opts = {}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(liveurl, download=False)
            live_status = info["live_status"].rstrip("\n")
            return True if live_status == "is_live" else False
