import PySimpleGUI as sg
import os
import sys

import mylogger
import traceback
import datetime
import glob
import pyocr

# ログの定義
logger = mylogger.setup_logger(__name__)


class MainForm:
    def __init__(self):

        # デザインテーマの一覧確認
        # sg.preview_all_look_and_feel_themes()

        # デザインテーマの設定
        sg.theme('BlueMono')

        # 設定ファイルのパス
        self.default_file = os.path.dirname(sys.argv[0]) + '\設定ファイル.xlsx'

        # ウィンドウの部品とレイアウト
        tab1_layout = [
            [sg.Text('設定ファイルのパスを指定してWEBサイトの取得を実行してください')],
            [sg.Text('設定ファイル', size=(11, 1)), sg.Input(self.default_file, key='inputFilePath'), sg.FileBrowse('ファイルを選択', key='inputFilePath1', target='inputFilePath')],
            [sg.Text(size=(40, 1), justification='center', text_color='#191970', key='message_text1'), sg.Button('取得実行', key='scrapy_execute')]
        ]

        tab2_layout = [
            [sg.Text('取得対象のチャンネルまたは再生リストのURLを指定して実行してください')],
            [sg.Text('YoutubeのURL', size=(11, 1)), sg.Input(size=(51, 1), key='video_url')],
            [sg.Text(size=(15, 1)), sg.Radio('チャンネルから取得', 1, key='channel_mode', default=True), sg.Radio('再生リストから取得', 1, key='playlist_mode')],
            # [sg.Text(size=(51, 1), justification='center', text_color='#191970', key='message_text2')],
            [sg.Text(size=(25, 1), justification='center', text_color='#191970', key='message_text2'),
             sg.Button('動画の文字起こし', key='video_ocr'), sg.Button('動画ダウンロード', key='video_download')]
        ]

        tab3_layout = [
            [sg.Text('検索ワードを入力して実行してください')],
            # [sg.Radio('youtube', 2, key='youtube', default=True), sg.Radio('ニコニコ', 2, key='niconico')],
            [sg.Text('検索ワード', size=(10, 1)), sg.Input(size=(52, 1), key='search_word')],
            # [sg.Checkbox('顔が含まれる動画を除外', key='chk_face', default=False), sg.Checkbox('文字が含まれる動画を除外', key='chk_letter', default=False)],
            [sg.Text(size=(41, 1), justification='center', text_color='#191970', key='message_text3'), sg.Button('動画ダウンロード', key='video_search')]
        ]

        tab4_layout = [
            [sg.Text('画像ファイルが格納されたフォルダを指定して実行してください')],
            [sg.Text('フォルダ', size=(8, 1)), sg.Input(key='inputFolderPath'), sg.FolderBrowse('フォルダを選択', key='inputFolder4', target='inputFolderPath')],
            [sg.Text(size=(40, 1), justification='center', text_color='#191970', key='message_text4'), sg.Button('出力実行', key='ocr_image_execute')]
        ]

        main_layout = [
            [sg.TabGroup([[sg.Tab('WEBサイト記事収集', tab1_layout),
                        sg.Tab('動画文字起こし', tab2_layout),
                        sg.Tab('動画検索ダウンロード', tab3_layout),
                        sg.Tab('画像文字起こし', tab4_layout)
                        ]])]
        ]

        # ウィンドウの生成
        window = sg.Window('WEBサイト・動画収集', main_layout)

        # イベントループ
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED:
                # ウィンドウのXボタンを押したときの処理
                break

            if event == 'scrapy_execute':
                # クローリングが選択された場合
                setting_file_path = values['inputFilePath']
                if setting_file_path == '':
                    setting_file_path = self.default_file

                # ファイル存在確認
                if not os.path.exists(setting_file_path):
                    logger.error("指定したパスに設定ファイルが存在しません。ファイル：" + setting_file_path)
                    sg.popup_error('指定したパスに設定ファイルが存在しません。', title='エラー', button_color=('#f00', '#ccc'))
                    continue

                # 拡張子チェック
                filepath, ext = os.path.splitext(setting_file_path)
                if not ext == '.xlsx':
                    logger.error('指定したファイルがExcelファイルではありません。ファイル：' + setting_file_path)
                    sg.popup_error('指定したファイルがExcelファイルではありません。', title='エラー', button_color=('#f00', '#ccc'))
                    continue

                # 実行
                self.execute_scrapy(setting_file_path)
                sg.Popup('処理が完了しました', title='実行結果')

            if event == 'video_ocr' or event == 'video_download':
                # 文字起こしが選択された場合
                if not values['video_url']:
                    logger.error('URLを指定してください')
                    continue

                video_url = values['video_url']
                # URLタイプ（1：チャンネル指定、2：再生リスト指定）
                url_type = 1
                channel_str = 'youtube.com/channel/'
                playlist_str = 'youtube.com/playlist?list='
                out_path = './output/'
                dt_now = datetime.datetime.now()
                now_str = dt_now.strftime('%Y-%m-%d_%H%M%S')

                if event == 'video_ocr':
                    out_path += 'sound/'
                elif event == 'video_download':
                    out_path += 'video/'

                if values['channel_mode']:
                    logger.info('チャンネルを指定')
                    url_type = 1
                    out_path += 'channel/' + now_str
                    if not channel_str in video_url:
                        logger.error('指定したURLが正しくありません。YoutubeのチャンネルのURLを指定してください')
                        sg.popup_error('指定したURLが正しくありません。YoutubeのチャンネルのURLを指定してください', title='エラー', button_color=('#f00', '#ccc'))
                        continue

                elif values['playlist_mode']:
                    logger.info('再生リストを指定')
                    url_type = 2
                    out_path += 'playlist/' + now_str
                    if not playlist_str in video_url:
                        logger.error('指定したURLが正しくありません。Youtubeの再生リストのURLを指定してください')
                        sg.popup_error('指定したURLが正しくありません。Youtubeの再生リストのURLを指定してください', title='エラー', button_color=('#f00', '#ccc'))
                        continue

                if event == 'video_ocr':
                    self.execute_youtube_ocr(url_type, video_url, out_path)
                elif event == 'video_download':
                    self.execute_youtube_download(url_type, video_url, out_path)

                sg.popup_notify('処理が完了しました', title='実行結果')
                sg.Popup('処理が完了しました', title='実行結果')

            if event == 'video_search':
                # キーワード動画検索
                search_word = values['search_word']
                # face_chk = values['chk_face']
                face_chk = False
                if not search_word:
                    logger.error('検索キーワードを入力してください')
                    sg.popup_error('検索キーワードを入力してください', title='エラー', button_color=('#f00', '#ccc'))
                    continue

                dt_now = datetime.datetime.now()
                now_str = dt_now.strftime('%Y-%m-%d_%H%M%S')
                out_path = './output/video/keyword/' + search_word + '/' + now_str
                self.execute_youtube_search(search_word, out_path, face_chk)
                sg.Popup('処理が完了しました', title='実行結果')

            if event == 'ocr_image_execute':
                target_folder = values['inputFolderPath']
                # 指定したフォルダから画像ファイル取得（BMP, PNM, PNG, JFIF, JPEG, TIFF）
                image_list = []
                image_list = check_image_ext(target_folder)

                if not len(image_list):
                    logger.error('指定したフォルダに画像ファイル（BMP, PNM, PNG, JFIF, JPEG, TIFF）がありません。')
                    sg.popup_error('指定したフォルダに画像ファイルがありません。', title='エラー', button_color=('#f00', '#ccc'))
                    continue

                # OCRツールがあるかチェック
                tools = pyocr.get_available_tools()
                if len(tools) != 0:
                    logger.error("OCRツールが見つかりませんでした。")
                    sg.popup_error('OCRツールが見つかりませんでした。', title='エラー', button_color=('#f00', '#ccc'))
                    continue

                dt_now = datetime.datetime.now()
                now_str = dt_now.strftime('%Y-%m-%d_%H%M%S')
                out_path = './output/image_ocr/' + now_str + '/'
                self.execute_ocr_image(image_list, out_path)
                sg.Popup('処理が完了しました', title='実行結果')

        window.close()


    def execute_scrapy(self, file_path):
            '''
            クローリングの実行
            '''
            try:
                logger.info("クローリングの処理開始")

                import excel_setting
                import launch_scrapy
                from blog_scrapy_item import ScrapyItems

                # 検索リストファイルの読み込み（全て欠損値がある行は読み込まない）
                excel_file_path = os.path.join(os.path.dirname(sys.argv[0]), file_path)
                setting_df = excel_setting.read_excel_setting(excel_file_path, "設定", 0, "A:D")

                item_list = []
                url_list = []
                for i in range(0, len(setting_df)):
                    site_name = setting_df.iloc[i]['サイト名']
                    exclusion_str = setting_df.iloc[i]['除外ワード']
                    url = setting_df.iloc[i]['URL']
                    if url:
                        url_list.append(url)

                    _item = ScrapyItems(site_name, url, exclusion_str)
                    item_list.append(_item)

                launch_scrapy.execute_spider(url_list, item_list)
                logger.info("クローリングの処理完了")
                return True

            except Exception as err:
                logger.error("クローリングの処理が失敗しました。")
                logger.error(err)
                logger.error(traceback.format_exc())
                return False


    def execute_youtube_ocr(self, url_type, video_url, out_path):
        '''
        動画の音声ファイルのダウンロード＋文字起こしを実行する
        '''
        try:
            logger.info("動画の音声ファイルをダウンロードの処理開始")
            logger.info("URLタイプ：" + str(url_type))
            logger.info("URL：" + video_url)
            logger.info("出力パス：" + out_path)

            import youtube
            import voice_recognition as voice

            # 音声のダウンロード
            file_list = []
            file_list = youtube.download_youtube(2, url_type, video_url, out_path)
            logger.info("動画の音声ファイルをダウンロードの処理完了")
            logger.info("音声ファイルの文字起こしの処理開始")
            voice.execute_voice_recognize(out_path)
            logger.info("音声ファイルの文字起こしの処理完了")
            return True

        except Exception as err:
            logger.error("動画の音声ファイル文字起こし処理が失敗しました。")
            logger.error(err)
            logger.error(traceback.format_exc())
            return False


    def execute_youtube_download(self, url_type, video_url, out_path):
        '''
        動画ファイルをダウンロードを実行する
        '''
        try:
            logger.info("動画ファイルダウンロードの処理開始")
            logger.info("URLタイプ：" + str(url_type))
            logger.info("URL：" + video_url)
            logger.info("出力パス：" + out_path)

            import youtube
            import voice_recognition as voice

            # 動画のダウンロード
            youtube.download_youtube(1, url_type, video_url, out_path)
            logger.info("動画ファイルダウンロードの処理完了")
            return True

        except Exception as err:
            logger.error("動画のダウンロード処理が失敗しました。")
            logger.error(err)
            logger.error(traceback.format_exc())
            return False


    def execute_youtube_search(self, search_word, out_path, face_chk):
        '''
        動画を検索し、ダウンロードする
        '''
        try:
            logger.info("動画の検索ダウンロードの処理開始")
            logger.info("検索キーワード：" + search_word)
            # logger.info("顔除外フラグ：" + str(face_chk))

            import youtube_data_api
            import excel_setting
            import youtube
            import face_recognition

            # APIキーの取得
            config_youtube_dic = excel_setting.read_config('YOUTUBE')
            api_key = config_youtube_dic['API_KEY']

            # 検索結果の取得
            logger.info("動画の検索処理開始")
            url_list = []
            url_list = youtube_data_api.execute_videos_search(search_word, api_key)
            logger.info("動画の検索処理完了")

            # ダウンロードの実行
            file_list = []
            logger.info("動画のダウンロード処理開始")
            file_list = youtube.download_youtube_urllist(url_list, out_path)
            logger.info("動画のダウンロード処理完了")
            if face_chk:
                logger.info("動画の顔判定処理開始")
                for file_path in file_list:
                    is_face = face_recognition.is_recognize_face_eye_video(file_path, True)
                    if is_face:
                        # 顔が検出されたらファイルを削除する
                        logger.debug("動画に顔が含まれるため削除。ファイル：" + file_path)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    else:
                        logger.debug("動画に顔が含まれないためそのまま。ファイル：" + file_path)

                logger.info("動画の顔判定処理完了")

            return True

        except Exception as err:
            logger.error("動画の検索ダウンロード処理が失敗しました。")
            logger.error(err)
            logger.error(traceback.format_exc())
            return False


    def execute_ocr_image(self, image_list: list, out_path: str):
            '''
            画像ファイルの文字認識を実行する
            '''
            try:
                logger.info("画像ファイルの文字認識の処理開始")
                logger.info("指定画像：" + ",".join(image_list))

                import ocr_image

                # 文字認識処理
                ocr_image.ocr_letter_image(image_list, 'jpn', out_path)
                logger.info("画像ファイルの文字認識の処理完了")
                return True

            except Exception as err:
                logger.error("画像ファイルの文字認識処理が失敗しました。")
                logger.error(err)
                logger.error(traceback.format_exc())
                return False


def expexpiration_date_check():
    import datetime
    now = datetime.datetime.now()
    expexpiration_datetime = now.replace(month=3, day=28, hour=12, minute=0, second=0, microsecond=0)
    logger.info("有効期限：" + str(expexpiration_datetime))
    if now < expexpiration_datetime:
        return True
    else:
        return False


def check_image_ext(target_dir: str):
    import re
    # 画像ファイルリスト
    image_list = []

    # 拡張子(正規表現)（BMP, PNM, PNG, JFIF, JPEG, and TIFF）
    CHECK_EXT = "\.(jp(e)?g|bmp|png|ppm|pgm|pbm|pnm|tiff|tif)$"

    # ファイルのみの一覧を取得
    files = [p for p in glob.glob(target_dir + '/**', recursive=True) if os.path.isfile(p)]

    # ファイルの件数が0の場合
    if len(files) == 0:
        return False

    # ファイルの一覧の拡張子を個別に確認
    for file in files:
        if not re.search(CHECK_EXT, file, re.IGNORECASE):
            continue
        else:
            image_list.append(file)

    return image_list


if __name__ == "__main__":
    args = sys.argv
    logger.info('プログラム起動開始')

    # 有効期限チェック
    if not (expexpiration_date_check()):
        logger.info("有効期限切れため、プログラム起動終了")
        sys.exit(0)

    if len(args) > 1:
        logger.info('引数あり。引数：' + args[1])
        if args[1] == "-s":
            # 引数がある場合、サイレントでクローリングを実行
            logger.info('バックグラウンドクローリングの処理開始')
            app = MainForm()

            # 設定ファイルのパス
            setting_file = os.path.dirname(sys.argv[0]) + '\設定ファイル.xlsx'
            app.execute_scrapy(setting_file)
            logger.info('バックグラウンドクローリングの処理完了')
            pass
        else:
            logger.info('引数が正しくありません。')
    else:
        # 引数なしの場合
        app = MainForm()
