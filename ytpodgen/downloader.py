import yt_dlp


from loguru import logger

def download(title, liveurl):
    if _is_live(liveurl):
        live_from_start = True
    else:
        live_from_start = False
    
    ydl_opts = {
        'format': 'bestaudio',
        'wait_for_video': (600, 3600), #(min_sec, max_sec) 
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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(liveurl)

def _is_live(liveurl):
    # ℹ️ See help(yt_dlp.YoutubeDL) for a list of available options and public functions
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(liveurl, download=False)
            live_status = info['live_status'].rstrip('\n')
            if live_status == 'is_live':
                return True
        except:
                return False
