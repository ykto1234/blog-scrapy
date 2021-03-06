from apiclient.discovery import build

# API情報
# DEVELOPER_KEY = 'AIzaSyCF7fF11xmrIbzrF1xXpOffyurbhPcfCz0'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def get_videos_search(keyword, api_key):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=api_key)
    youtube_query = youtube.search().list(q=keyword, part='id,snippet', maxResults=10)
    youtube_res = youtube_query.execute()
    return youtube_res.get('items', [])

def execute_videos_search(keyword, api_key):
    url_list = []
    results = get_videos_search(keyword, api_key)
    for item in results:
        if item['id']['kind'] == 'youtube#video':
            title = item['snippet']['title']
            url = 'https://www.youtube.com/watch?v=' + item['id']['videoId']
            print(item['snippet']['title'])
            print('https://www.youtube.com/watch?v=' + item['id']['videoId'])
            url_list.append(url)

    return url_list