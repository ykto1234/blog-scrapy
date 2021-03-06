import youtube_dlc
import json
import time
import random
import os
import sys


def download_video(download_opts, urlnum, urllist, out_path, ext_str):
    file_list = []
    with youtube_dlc.YoutubeDL(download_opts) as ydl:
        i = 0
        for url in urllist:
            while True:
                try:
                    info_dict = ydl.extract_info(url, download=True)
                    o = json.loads(json.dumps(info_dict, ensure_ascii=False))
                    file_path = out_path + '/' + o['title'] + '/' + o['title'] + ext_str
                    file_list.append(file_path)
                    wait_time(5, 10)
                except KeyboardInterrupt:
                    print("\nKeyboardInterrupt")
                    exit(1)
                except youtube_dlc.utils.YoutubeDLError:
                    youtube_dlc.utils.std_headers['User-Agent']=youtube_dlc.utils.random_user_agent()
                    wait_time(1, 10)
                except:
                    print("\nother error")
                    exit(1)
                else:
                    youtube_dlc.utils.std_headers['User-Agent']=youtube_dlc.utils.random_user_agent()
                    i += 1
                    print(
                        "\n\nDownloaded Items " + str(i) + "/" + str(urlnum) + "\n\n"
                        "--------------------------------------------------------------"
                    )
                    break

        return file_list


def flat_playlist(flat_list, playlist_url):
    with youtube_dlc.YoutubeDL(flat_list) as ydl:
        try:
            info_dict = ydl.extract_info(playlist_url, download=False)
        except youtube_dlc.utils.YoutubeDLError as youtube_err:
            print("\nNot get playlist. Check playlist-id and retry")
            raise youtube_err
            # exit(1)
        except:
            print("\nother error")
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
            print("\nNot get playlist. Check playlist-id and retry")
            raise youtube_err
            # exit(1)
        except:
            print("\nother error")
            raise Exception
            # exit(1)
        o = json.loads(json.dumps(info_dict, ensure_ascii=False))
    url = ""
    url = o["url"]
    return url


def wait_time(s, e):
    sleeptime = random.randrange(s, e) + random.random()
    print("wait for " + str(f"{sleeptime:.1f}"))
    time.sleep(sleeptime)


def download_youtube_urllist(url_list: [], out_path: str):
    mp4_download_opts = {
        'outtmpl': out_path + "/%(title)s/%(title)s.%(ext)s",
        'format':'136'
    }

    download_opts = mp4_download_opts

    return download_video(download_opts, len(url_list), url_list, out_path, '.mp4')


def download_youtube(download_mode, url_type, video_url, out_path):

    if not os.path.exists(out_path):
        print("Make output directory --> " + out_path)
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

    print(
        "--------------------------------------------------------------\n"
        "\ndownload items " + str(urlnum) + "\n"
        "download start\n\n"
        "--------------------------------------------------------------"
    )

    mp4_download_opts = {
        'outtmpl': out_path + "/%(title)s/%(title)s.%(ext)s",
        'format':'136'
    }

    wav_download_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_path + "/%(title)s/%(title)s.%(ext)s",
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
        print("Make output directory --> " + outputpath)
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

    print("\nDownload complete\n")
