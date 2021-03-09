import pyocr
import pyocr.builders
import cv2
from PIL import Image
import sys
import time
import os

import mylogger

# ログの定義
logger = mylogger.setup_logger(__name__)


def ocr_letter_image(image_path_list: list, target_lang: str, out_path: str):
    #利用可能なOCRツールを取得
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        logger.error("OCRツールが見つかりませんでした。")
        raise Exception("OCRツールが見つかりませんでした。")
        # sys.exit(1)

    #利用可能なOCRツールはtesseractしか導入していないため、0番目のツールを利用
    tool = tools[0]

    for image_file in image_path_list:
        txt = tool.image_to_string(
            Image.open(image_file),
            lang = target_lang,
            builder = pyocr.builders.TextBuilder()
            # builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6)
        )
        os.makedirs(out_path, exist_ok=True)
        basename_without_ext = os.path.splitext(os.path.basename(image_file))[0]
        with open(out_path + basename_without_ext + '.txt', 'w') as f:
            f.write(txt)


def ocr_letter_image2(image_path_list: list, target_lang: str):

    # 利用可能なOCRツールを取得
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        logger.error("OCRツールが見つかりませんでした。")
        raise Exception("OCRツールが見つかりませんでした。")
        # sys.exit(1)

    # OCRエンジンの取得
    tools = pyocr.get_available_tools()
    tool = tools[0]

    for image_path in image_path_list:

        # 原稿画像の読み込み
        img_org = Image.open(image_path)
        img_rgb = img_org.convert("RGB")
        pixels = img_rgb.load()

        # 原稿画像加工（黒っぽい色以外は白=255,255,255にする）
        c_max = 169
        for j in range(img_rgb.size[1]):
            for i in range(img_rgb.size[0]):
                if (pixels[i, j][0] > c_max or pixels[i, j][1] > c_max or
                        pixels[i, j][0] > c_max):
                    pixels[i, j] = (255, 255, 255)

        # ＯＣＲ実行
        builder = pyocr.builders.TextBuilder()
        result = tool.image_to_string(img_rgb, lang=target_lang, builder=builder)

    print(result)

if __name__ == '__main__':
    imgage_list = ['./tmp/ocr-test.png']
    ocr_letter_image(imgage_list, 'jpn')
    # ocr_letter_image2(imgage_list, 'jpn')