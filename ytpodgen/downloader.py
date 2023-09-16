import yt_dlp


class Downloader:
    def __init__(self):
        pass

    @staticmethod
    def download(title, liveurl):
        live_from_start = False
        
        # See help(yt_dlp.YoutubeDL) for a list of available options
        # and public functions
        # https://github.com/yt-dlp/yt-dlp/blob/216bcb66d7dce0762767d751dad10650cb57da9d/yt_dlp/YoutubeDL.py#L184
        ydl_opts = {
            # best audio-only format if available,
            # and if not, fall back to best format that contains both video and audio
            "format": "bestaudio/best",
            "wait_for_video": (60, 600),
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

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(liveurl)
