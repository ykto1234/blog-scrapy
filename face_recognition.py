import cv2
import os
import time


def recognize_face_eye_video(target_video_path, eye_recognize_flg):
    # eye_recognize_flgが「True：顔と目を認識する」、「False：顔のみ認識する」
    cap = cv2.VideoCapture(target_video_path)

    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    writer = cv2.VideoWriter('detect_face.mp4',fourcc, fps, (cap_width, cap_height))

    cascade_base_path = "./face_recognition_data/"
    # カスケードを取得
    # face_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_frontalface_alt_tree.xml'))
    face_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_frontalface_default.xml'))
    right_eye_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_righteye_2splits.xml'))
    left_eye_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_lefteye_2splits.xml'))
    upperbody_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_upperbody.xml'))
    fullbody_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_fullbody.xml'))

    start = time.time()

    try :
        while True:

            if not cap.isOpened():
                break

            ret, frame = cap.read()

            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # フレームの中に顔が写っている　
            face_points = face_cascade.detectMultiScale(img_gray)

            for (fx,fy,fw,fh) in face_points:

                # ROI(Region of Interest:対象領域)となる画像を切り出す
                if eye_recognize_flg:
                    # 右領域と左領域でそれぞれ分割(アシュラ男爵方式)
                    width_center = fx + int(fw * 0.5)
                    face_right_gray = img_gray[fy:fy+fh, fx:width_center]
                    face_left_gray = img_gray[fy:fy+fh, width_center:fx+fw]
                    # 右目と左目の両方が写っているか判定
                    right_eye_points = right_eye_cascade.detectMultiScale(face_right_gray)
                    left_eye_points = left_eye_cascade.detectMultiScale(face_left_gray)

                    if 0 < len(right_eye_points) and 0 < len(left_eye_points):
                        (rx,ry,rw,rh) = right_eye_points[0]
                        (lx,ly,lw,lh) = left_eye_points[0]

                        # 顔と右目と左目を四角形で囲む
                        # 右目はオレンジ
                        cv2.rectangle(frame,(fx+rx,fy+ry),(fx+rx+rw,fy+ry+rh),(0,255,255),2)
                        # 左目は赤
                        cv2.rectangle(frame,(width_center+lx,fy+ly),(width_center+lx+lw,fy+ly+lh),(0,0,255),2)

                # 顔全体は緑
                cv2.rectangle(frame,(fx,fy),(fx+fw,fy+fh),(0,255,0),2)

                # # フレームの中に全身が写っている　
                # fullbody_points = fullbody_cascade.detectMultiScale(img_gray)

                # for (bx,by,bw,bh) in fullbody_points:
                #     # 全身は
                #     cv2.rectangle(frame,(bx,by),(bx+bw,by+bh),(0,255,255),2)

                writer.write(frame)

    except cv2.error as e:
        print(e)

    print("処理時間 {} 秒".format(time.time() - start))
    writer.release()
    cap.release()


def is_recognize_face_eye_video(target_video_path, eye_recognize_flg):
    # eye_recognize_flgが「True：顔と目を認識する」、「False：顔のみ認識する」
    face_flg = False

    cap = cv2.VideoCapture(target_video_path)
    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    cascade_base_path = "./face_recognition_data/"
    # カスケードを取得
    face_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_frontalface_default.xml'))
    right_eye_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_righteye_2splits.xml'))
    left_eye_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_lefteye_2splits.xml'))
    upperbody_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_upperbody.xml'))
    fullbody_cascade = cv2.CascadeClassifier(os.path.join(cascade_base_path, 'haarcascade_fullbody.xml'))

    try :

        face_cnt = 0

        while True:
            if not cap.isOpened():
                return False

            ret, frame = cap.read()

            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # フレームの中に顔が写っている　
            face_points = face_cascade.detectMultiScale(img_gray)

            for (fx,fy,fw,fh) in face_points:
                # 顔検出されたキャプチャが5以上の場合、顔があると判断

                if eye_recognize_flg:
                    # ROI(Region of Interest:対象領域)となる画像を切り出す
                    # 右領域と左領域でそれぞれ分割(アシュラ男爵方式)
                    width_center = fx + int(fw * 0.5)
                    face_right_gray = img_gray[fy:fy+fh, fx:width_center]
                    face_left_gray = img_gray[fy:fy+fh, width_center:fx+fw]
                    # 右目と左目の両方が写っているか判定
                    right_eye_points = right_eye_cascade.detectMultiScale(face_right_gray)
                    left_eye_points = left_eye_cascade.detectMultiScale(face_left_gray)

                    if 0 < len(right_eye_points) and 0 < len(left_eye_points):
                        face_cnt += 1
                        if face_cnt >= 5:
                            face_flg = True
                else:
                    face_cnt += 1
                    if face_cnt >= 5:
                        face_flg = True

            if face_flg:
                break

    except cv2.error as e:
        print(e)

    cap.release()
    return face_flg


def check_face_eye_image(target_image_path):
    # Haar-like特徴分類器の読み込み
    cascade_base_path = "./face_recognition_data/"
    face_cascade = cv2.CascadeClassifier(cascade_base_path + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cascade_base_path + 'haarcascade_eye.xml')

    # イメージファイルの読み込み
    img = cv2.imread(target_image_path)

    # グレースケール変換
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 顔を検知
    faces = face_cascade.detectMultiScale(gray)
    for (x,y,w,h) in faces:
        # 検知した顔を矩形で囲む
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        # 顔画像（グレースケール）
        roi_gray = gray[y:y+h, x:x+w]
        # 顔ｇ増（カラースケール）
        roi_color = img[y:y+h, x:x+w]
        # 顔の中から目を検知
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            # 検知した目を矩形で囲む
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

    # 画像表示
    cv2.imshow('img',img)

    # 何かキーを押したら終了
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    VIDEO_PATH = "./output/video/playlist/video/住宅ローンは闇。 #Shorts/住宅ローンは闇。 #Shorts.mp4"
    recognize_face_eye_video(VIDEO_PATH, False)