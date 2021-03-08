import youtube_dlc
import json
import time
import random
import os
import sys

import mylogger

# ログの定義
logger = mylogger.setup_logger(__name__)


def download_video(download_opts, urlnum, urllist, out_path, ext_str):
    file_list = []
    with youtube_dlc.YoutubeDL(download_opts) as ydl:
        i = 0
        count = 1
        max_retry_count = 3
        for url in urllist:
            while True:
                try:
                    info_dict = ydl.extract_info(url, download=True)
                    o = json.loads(json.dumps(info_dict, ensure_ascii=False))
                    file_path = out_path + '/' + o['uploader'] + '/' + o['title'] + ext_str
                    file_list.append(file_path)
                    wait_time(5, 8)
                except KeyboardInterrupt:
                    logger.info("\nKeyboardInterrupt")
                    return file_list
                    # exit(1)
                except youtube_dlc.utils.YoutubeDLError as you_err:
                    logger.error(you_err)
                    logger.error('url:' + url)
                    count += 1
                    if count >= max_retry_count:
                        break
                    youtube_dlc.utils.std_headers['User-Agent']=youtube_dlc.utils.random_user_agent()
                    wait_time(1, 8)
                except:
                    logger.error("\nother error")
                    break
                    # exit(1)
                else:
                    youtube_dlc.utils.std_headers['User-Agent']=youtube_dlc.utils.random_user_agent()
                    i += 1
                    logger.debug("Downloaded: " + o['title'])
                    logger.debug("Downloaded Items " + str(i) + "/" + str(urlnum))
                    break

        return file_list


def flat_playlist(flat_list, playlist_url):
    with youtube_dlc.YoutubeDL(flat_list) as ydl:
        try:
            info_dict = ydl.extract_info(playlist_url, download=False)
        except youtube_dlc.utils.YoutubeDLError as youtube_err:
            logger.info("\nNot get playlist. Check playlist-id and retry")
            raise youtube_err
            # exit(1)
        except:
            logger.error("\nother error")
            raise Exception
            # exit(1)
        o = json.loads(json.dumps(info_dict, ensure_ascii=False))
    urllist = []
    for items in o["entries"]:
        urllist.append("https://www.youtube.com/watch?v=" + items["id"])
    urlnum = len(urllist)
    return urlnum, urllist


def flat_channel(flat_list, channel_url):
    with youtube_dlc.YoutubeDL(flat_list) as ydl:
        try:
            info_dict = ydl.extract_info(channel_url, download=False)
        except youtube_dlc.utils.YoutubeDLError as youtube_err:
            logger.info("\nNot get playlist. Check playlist-id and retry")
            raise youtube_err
            # exit(1)
        except:
            logger.error("\nother error")
            raise Exception
            # exit(1)
        o = json.loads(json.dumps(info_dict, ensure_ascii=False))
    url = ""
    url = o["url"]
    return url


def wait_time(s, e):
    sleeptime = random.randrange(s, e) + random.random()
    logger.debug("wait for " + str(f"{sleeptime:.1f}"))
    time.sleep(sleeptime)


def download_youtube_urllist(url_list: [], out_path: str):
    mp4_download_opts = {
        'outtmpl': out_path + "/%(uploader)s/%(title)s.%(ext)s",
        'format':'136+140'
    }

    download_opts = mp4_download_opts

    return download_video(download_opts, len(url_list), url_list, out_path, '.mp4')


def download_youtube(download_mode, url_type, video_url, out_path):

    if not os.path.exists(out_path):
        logger.debug("Make output directory --> " + out_path)
        os.makedirs(out_path)

    flat_list = {
        "extract_flat": True,
    }

    if url_type == 1:
        # チャンネル指定の場合
        playlist_url = flat_channel(flat_list, video_url)
        urlnum,urllist = flat_playlist(flat_list, playlist_url)
    else:
        # 再生リスト指定の場合
        playlist_url = video_url
        urlnum,urllist = flat_playlist(flat_list, playlist_url)

    logger.debug(
        "\n--------------------------------------------------------------\n"
        "download items " + str(urlnum) + "\n"
        "download start\n"
        "--------------------------------------------------------------"
    )

    mp4_download_opts = {
        'outtmpl': out_path + "/%(uploader)s/%(title)s.%(ext)s",
        'format':'136+140'
    }

    wav_download_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_path + "/%(uploader)s/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "256",
            }
        ],
    }
    download_opts = mp4_download_opts
    ext_str = '.mp4'
    if download_mode == 2:
        # 音声ダウンロードの場合
        download_opts = wav_download_opts
        ext_str = '.wav'

    return download_video(download_opts, urlnum, urllist, out_path, ext_str)


if __name__ == "__main__":

    try:
        #playlist = "https://www.youtube.com/playlist?list="+sys.argv[1]
        #outputpath = "./"+sys.argv[2]
        playlist_url = "https://www.youtube.com/playlist?list=PLbPWOEToFIVvJ1kWpNp-KVIbLGQzR5Kr4"
        channel_url = "https://www.youtube.com/channel/UCaFLeZCNpcIafSFSayv9ksg"
        outputpath = "./output/video"
    except IndexError:
        print("Arguments are playlist-id output-path")
        exit(1)


    if not os.path.exists(outputpath):
        logger.debug("Make output directory --> " + outputpath)
        os.makedirs(outputpath)


    flat_list = {
        "extract_flat": True,
    }
    # urlnum,urllist = flat_playlist(flat_list, playlist_url)
    playlist_url = flat_channel(flat_list, channel_url)
    urlnum,urllist = flat_playlist(flat_list, playlist_url)

    print(
        "--------------------------------------------------------------\n"
        "\ndownload items " + str(urlnum) + "\n"
        "download start\n\n"
        "--------------------------------------------------------------"
    )

    mp4_download_opts = {
        'outtmpl': outputpath + "/%(title)s/%(title)s.%(ext)s",
        'format':'136'
    }

    wav_download_opts = {
        "format": "bestaudio/best",
        "outtmpl": outputpath + "/%(title)s/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "256",
            }
        ],
    }
    ext_str = '.mp4'
    download_video(wav_download_opts, urlnum, urllist, outputpath, ext_str)

    logger.info("\nDownload complete\n")
