import speech_recognition as sr
from pydub import AudioSegment
import os


def text_formatter(file_path):
    # テキストファイルの" "を改行に変える
    outdir = os.path.dirname(file_path)
    out_file_path = outdir + "/result_lines.txt"
    with open(file_path, encoding="cp932") as f:
        data_lines = f.read()

    # 文字列置換
    data_lines = data_lines.replace(" ", "\n")

    # 同じファイル名で保存
    with open(out_file_path, mode="w", encoding="cp932") as f:
        f.write(data_lines)


def sound_recognize(sound_file_list):
    r = sr.Recognizer()
    out_text = ""
    outdir = os.path.dirname(sound_file_list[0])
    out_file_path = outdir + "/result.txt"
    if os.path.exists(out_file_path):
        os.remove(out_file_path)
    try:
        for sound_file in sound_file_list:
            with sr.AudioFile(sound_file) as source:
                r.adjust_for_ambient_noise(source)  # 雑音対策
                audio = r.record(source)
            text = r.recognize_google(audio, language='ja-JP')
            print(text)
            out_text += text

            with open(out_file_path, mode='w') as f:
                f.write(out_text)

    except sr.UnknownValueError:
        print("could not understand audio;")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    text_formatter(out_file_path)


def split_video_file(video_path):
    # wavファイルの読み込み
    sound = AudioSegment.from_file(video_path, format="wav")

    # 総再生時間(s)
    total_time_s = sound.duration_seconds
    print(total_time_s)
    # 総再生時間(ms)
    total_time_ms = total_time_s * 1000

    outfile_path_list = [] # type: List[outfile_path]

    start_time = 0
    file_num = 1
    # 1動画あたりの動画の長さ（ms）
    # Googleのspeech_recognitionが対応可能な長さが分からないため、一旦2分で定義
    time_per_one = 60 * 1000

    while True:
        # 定義した長さで動画を分割
        end_time = start_time + time_per_one
        outdir = os.path.dirname(video_path)
        outfile_path = outdir + "/sound" + str(file_num) + ".wav"
        if end_time < total_time_ms:
            sound[start_time : end_time].export(outfile_path, format="wav")
            outfile_path_list.append(outfile_path)
        else:
            sound[start_time :].export(outfile_path, format="wav")
            outfile_path_list.append(outfile_path)
            break

        start_time += time_per_one
        file_num += 1

    return outfile_path_list

def execute_voice_recognize(video_path_list):
    for video_path in video_path_list:
        outfile_path_list = split_video_file(video_path)
        sound_recognize(outfile_path_list)

        # ファイル削除
        for outfile_path in outfile_path_list:
            if os.path.exists(outfile_path):
                os.remove(outfile_path)


if __name__ == "__main__":
    outfile_path_list = split_video_file()
    sound_recognize(outfile_path_list)
    # ファイル削除
    for outfile_path in outfile_path_list:
        if os.path.exists(outfile_path):
            os.remove(outfile_path)