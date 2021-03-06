import PySimpleGUI as sg
import os
import sys

import mylogger
import traceback

# ログの定義
logger = mylogger.setup_logger(__name__)


class MainForm:
    def __init__(self):

        # sg.preview_all_look_and_feel_themes()

        # デザインテーマの設定
        sg.theme('BlueMono')

        # 設定ファイルのパス
        self.default_file = os.path.dirname(sys.argv[0]) + '\設定ファイル.xlsx'

        # ウィンドウの部品とレイアウト
        tab1_layout = [
            [sg.Text('指定した設定ファイルを読み込んでWEBサイトから記事を取得します')],
            [sg.Text('', size=(50, 1), key='message_text1')],
            [sg.Text('ファイル', size=(10, 1)), sg.Input(self.default_file, key='inputFilePath'), sg.FileBrowse('ファイルを選択', key='inputFilePath1')],
            [sg.Button('実行', key='scrapy_execute')]
        ]

        tab2_layout = [
            [sg.Text('取得対象のチャンネルまたは再生リストのURLを指定して実行してください')],
            [sg.Text(size=(50, 1), key='message_text2')],
            [sg.Text('URL', size=(3, 1)), sg.Input(key='video_url')],
            [sg.Radio('チャンネルから取得', 1, key='channel_mode', default=True), sg.Radio('再生リストから取得', 1, key='playlist_mode')],
            [sg.Button('動画から文字起こし実行', key='video_ocr'), sg.Button('動画ダウンロード実行', key='video_download')]
        ]

        tab3_layout = [
            [sg.Text('検索ワードを入力して実行してください')],
            [sg.Text(size=(50, 1), key='message_text3')],
            # [sg.Radio('youtube', 2, key='youtube', default=True), sg.Radio('ニコニコ', 2, key='niconico')],
            [sg.Text('検索ワード', size=(10, 1)), sg.Input(key='search_word')],
            # [sg.Checkbox('顔が含まれる動画を除外', key='chk_face', default=False), sg.Checkbox('文字が含まれる動画を除外', key='chk_letter', default=False)],
            [sg.Button('動画ダウンロード', key='video_search')]
        ]

        main_layout = [
            [sg.TabGroup([[sg.Tab('WEBサイト記事収集', tab1_layout),
                        sg.Tab('動画文字起こし', tab2_layout),
                        sg.Tab('動画検索ダウンロード', tab3_layout)
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
                    # window['message_text'].update('指定したパスに設定ファイルが存在しません。')
                    continue

                # 拡張子チェック
                filepath, ext = os.path.splitext(setting_file_path)
                if not ext == '.xlsx':
                    logger.error('指定したファイルがExcelファイルではありません。ファイル：' + setting_file_path)
                    sg.popup_error('指定したファイルがExcelファイルではありません。', title='エラー', button_color=('#f00', '#ccc'))
                    continue

                # 実行
                window['message_text1'].update('・・・実行中・・・')
                self.execute_scrapy(setting_file_path)
                window['message_text1'].update('')
                sg.Popup('処理が完了しました', title='実行結果')

            if event == 'video_ocr' or event == 'video_download':
                # 文字起こしが選択された場合
                # URL
                if not values['video_url']:
                    logger.error('URLを指定してください')
                    continue

                video_url = values['video_url']
                # URLタイプ（1：チャンネル指定、2：再生リスト指定）
                url_type = 1
                channel_str = 'youtube.com/channel/'
                playlist_str = 'youtube.com/playlist?list='
                out_path = './output/video/'

                if values['channel_mode']:
                    logger.info('チャンネルを指定')
                    url_type = 1
                    out_path += 'channel'
                    if not channel_str in video_url:
                        logger.error('指定したURLが正しくありません。YoutubeのチャンネルのURLを指定してください')
                        sg.popup_error('指定したURLが正しくありません。YoutubeのチャンネルのURLを指定してください', title='エラー', button_color=('#f00', '#ccc'))
                        continue

                elif values['playlist_mode']:
                    logger.info('再生リストを指定')
                    url_type = 2
                    out_path += 'playlist'
                    if not playlist_str in video_url:
                        logger.error('指定したURLが正しくありません。Youtubeの再生リストのURLを指定してください')
                        sg.popup_error('指定したURLが正しくありません。Youtubeの再生リストのURLを指定してください', title='エラー', button_color=('#f00', '#ccc'))
                        continue
                window['message_text2'].update('・・・実行中・・・')
                if event == 'video_ocr':
                    out_path += '/sound'
                    self.execute_youtube_ocr(url_type, video_url, out_path)
                elif event == 'video_download':
                    out_path += '/video'
                    self.execute_youtube_download(url_type, video_url, out_path)

                window['message_text2'].update('')
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

                window['message_text3'].update('・・・実行中・・・')
                out_path = './output/video/keyword/' + search_word
                self.execute_youtube_search(search_word, out_path, face_chk)
                window['message_text3'].update('')
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
                # excel_file_path = os.path.join(os.path.dirname(sys.argv[0]), "設定ファイル.xlsx")
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
                return True

            except Exception as err:
                # messagebox.showerror("実行結果", "処理が失敗しました。")
                logger.error("処理が失敗しました。")
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
            voice.execute_voice_recognize(file_list)
            return True

        except Exception as err:
            # messagebox.showerror("実行結果", "処理が失敗しました。")
            logger.error("動画の音声ファイルをダウンロード＋文字起こし処理が失敗しました。")
            logger.error(err)
            logger.error(traceback.format_exc())
            return False


    def execute_youtube_download(self, url_type, video_url, out_path):
        '''
        動画ファイルをダウンロードを実行する
        '''
        try:
            logger.info("動画の音声ファイルをダウンロードの処理開始")
            logger.info("URLタイプ：" + str(url_type))
            logger.info("URL：" + video_url)
            logger.info("出力パス：" + out_path)

            import youtube
            import voice_recognition as voice

            # 動画のダウンロード
            youtube.download_youtube(1, url_type, video_url, out_path)
            return True

        except Exception as err:
            # messagebox.showerror("実行結果", "処理が失敗しました。")
            logger.error("動画の音声ファイルをダウンロード＋文字起こし処理が失敗しました。")
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
            logger.info("顔除外フラグ：" + str(face_chk))

            import youtube_data_api
            import excel_setting
            import youtube
            import face_recognition

            # APIキーの取得
            config_youtube_dic = excel_setting.read_config('YOUTUBE')
            api_key = config_youtube_dic['API_KEY']

            # 検索結果の取得
            url_list = []
            url_list = youtube_data_api.execute_videos_search(search_word, api_key)

            # ダウンロードの実行
            file_list = []
            file_list = youtube.download_youtube_urllist(url_list, out_path)
            if face_chk:
                for file_path in file_list:
                    is_face = face_recognition.is_recognize_face_eye_video(file_path, True)

                    if is_face:
                        # 顔が検出されたらファイルを削除する
                        if os.path.exists(file_path):
                            os.remove(file_path)

            return True

        except Exception as err:
            # messagebox.showerror("実行結果", "処理が失敗しました。")
            logger.error("動画の音声ファイルをダウンロード＋文字起こし処理が失敗しました。")
            logger.error(err)
            logger.error(traceback.format_exc())
            return False


if __name__ == "__main__":
    args = sys.argv
    logger.info('プログラム起動開始')
    if len(args) > 1:
        logger.info('引数あり。引数：' + args[1])
        if args[1] == "-s":
            # 引数がある場合、サイレントでクローリングを実行
            logger.info('引数があったため、バックグラウンドでクローリングを実行します。')
            app = MainForm()
            app.execute_scrapy()
            pass
        else:
            logger.info('引数が正しくありません。')
    else:
        # 引数なしの場合
        app = MainForm()