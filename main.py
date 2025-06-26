import os
import time
import csv
from gtts import gTTS
import pygame
import tempfile


def load_words_from_csv(filename):
    """
    CSVファイルから英単語と日本語の対応を読み込む

    Args:
        filename (str): CSVファイルのパス

    Returns:
        list: [{'english': '英単語', 'japanese': '日本語'}, ...] の辞書リスト
    """
    words = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # ヘッダーの空白を除去
                english = row['english'].strip()
                japanese = row['japanese'].strip()
                words.append({'english': english, 'japanese': japanese})
    except FileNotFoundError:
        print(f"エラー: {filename} が見つかりません。")
        print("main.pyと同じ階層にword.csvを配置してください。")
        return []
    except Exception as e:
        print(f"CSVファイル読み込みエラー: {e}")
        return []

    return words


def play_words(word_data):
    """
    辞書リストから英単語を順番に3回ずつ再生する
    3回目の再生時に日本語を表示

    Args:
        word_data (list): [{'english': '英単語', 'japanese': '日本語'}, ...] の辞書リスト
    """
    # pygameの初期化
    pygame.mixer.init()

    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp()

    try:
        for word_info in word_data:
            english_word = word_info['english']
            japanese_word = word_info['japanese']

            print(f"再生中: {english_word}")

            # gTTSで音声ファイルを作成
            tts = gTTS(text=english_word, lang='en')
            temp_file = os.path.join(temp_dir, f"{english_word}.mp3")
            tts.save(temp_file)

            # 同じ単語を3回再生
            for i in range(3):
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()

                # 3回目の再生時に日本語を表示
                if i == 2:  # 3回目（0, 1, 2のインデックス）
                    print(f"  → 意味: {japanese_word}")

                # 再生が完了するまで待機
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                # 3回目でなければ間隔をあける
                if i < 2:
                    time.sleep(0.7)

            # 次の単語との間隔
            time.sleep(0.7)

            # 一時ファイルを削除
            os.remove(temp_file)

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    finally:
        # 一時ディレクトリをクリーンアップ
        try:
            os.rmdir(temp_dir)
        except:
            pass

        # pygameを終了
        pygame.mixer.quit()


def main():
    # CSVファイルから英単語データを読み込み
    csv_filename = "word.csv"
    word_data = load_words_from_csv(csv_filename)

    if not word_data:
        print("単語データの読み込みに失敗しました。プログラムを終了します。")
        return

    print("英単語の音声再生を開始します...")
    print("各単語を3回ずつ再生し、3回目の再生時に日本語を表示します。")
    print("単語間に0.7秒の間隔をあけます。")
    print(f"読み込んだ単語数: {len(word_data)}語")
    print("-" * 50)

    play_words(word_data)

    print("-" * 50)
    print("すべての単語の再生が完了しました。")


if __name__ == "__main__":
    main()
