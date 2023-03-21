from yt_dlp import YoutubeDL


from loguru import logger

def download(title, liveurl):
    if _is_live(liveurl):
        live_from_start = True
    else:
        live_from_start = False
    
    # See help(yt_dlp.YoutubeDL) for a list of available options and public functions
    # https://github.com/yt-dlp/yt-dlp/blob/216bcb66d7dce0762767d751dad10650cb57da9d/yt_dlp/YoutubeDL.py#L184
    ydl_opts = {
        'format': 'bestaudio/best', # best audio-only format if available, if not, fall back to best format that contains both video and audio
        'wait_for_video': (60, 60), 
        'outtmpl': f'{title}_%(epoch>%Y%m%d%H%M%S)s_%(id)s',
        'live_from_start': live_from_start,
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '64'
        }],
        'postprocessor_args': [
            '-ac', '1', # audio channel mono
        ],
    }

    with YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(liveurl)

def _is_live(liveurl):
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(liveurl, download=False)
            live_status = info['live_status'].rstrip('\n')
            if live_status == 'is_live':
                return True
        except:
                return False
