from googleapiclient.discovery import build
import mylogger

# ログの定義
logger = mylogger.setup_logger(__name__)

# API情報
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def get_videos_search(keyword, api_key):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)
    youtube_query = youtube.search().list(q=keyword, part='id,snippet', maxResults=50)
    youtube_res = youtube_query.execute()
    return youtube_res.get('items', [])

def execute_videos_search(keyword, api_key):
    url_list = []
    results = get_videos_search(keyword, api_key)
    for item in results:
        if item['id']['kind'] == 'youtube#video':
            title = item['snippet']['title']
            url = 'https://www.youtube.com/watch?v=' + item['id']['videoId']
            # UnicodeDecodeErrorの回避
            title_byte = title.encode('cp932', 'ignore')
            title_str = title_byte.decode('cp932')
            logger.debug(title_str)
            logger.debug('https://www.youtube.com/watch?v=' + item['id']['videoId'])
            url_list.append(url)

    return url_list