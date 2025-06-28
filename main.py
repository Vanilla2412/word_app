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


def get_target_word_count(total_words):
    """
    今日再生する単語数を入力で取得する

    Args:
        total_words (int): CSVファイル内の総単語数

    Returns:
        int: 今日再生する単語数
    """
    while True:
        try:
            print(f"CSVファイル内の総単語数: {total_words}語")
            target_count = int(input("今日再生する単語数を入力してください: "))

            if target_count <= 0:
                print("1以上の数値を入力してください。")
                continue
            elif target_count > total_words:
                print(f"入力された数値が総単語数({total_words}語)を超えています。")
                print(f"最大{total_words}語まで設定できます。")
                continue
            else:
                return target_count
        except ValueError:
            print("有効な数値を入力してください。")


def play_words(word_data, target_count):
    """
    辞書リストから英単語を順番に3回ずつ再生する
    3回目の再生時に日本語を表示
    指定した単語数に達したらストップ

    Args:
        word_data (list): [{'english': '英単語', 'japanese': '日本語'}, ...] の辞書リスト
        target_count (int): 今日再生する単語数
    """
    # pygameの初期化
    pygame.mixer.init()

    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp()

    try:
        played_count = 0

        for word_info in word_data:
            # 目標単語数に達したらストップ
            if played_count >= target_count:
                print(f"\n目標の{target_count}語に達しました。プログラムを終了します。")
                break

            english_word = word_info['english']
            japanese_word = word_info['japanese']
            played_count += 1

            print(f"再生中: {english_word} ({played_count}/{target_count})")

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

    except KeyboardInterrupt:
        print(f"\n\nプログラムが中断されました。")
        print(f"再生完了: {played_count}/{target_count}語")
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

    total_words = len(word_data)
    print("=" * 60)
    print("英単語学習プログラム")
    print("=" * 60)

    # 今日再生する単語数を取得
    target_count = get_target_word_count(total_words)

    print("\n" + "-" * 60)
    print("英単語の音声再生を開始します...")
    print("各単語を3回ずつ再生し、3回目の再生時に日本語を表示します。")
    print("単語間に0.7秒の間隔をあけます。")
    print(f"今日の目標: {target_count}語")
    print("-" * 60)

    play_words(word_data, target_count)

    print("-" * 60)
    print("プログラムを終了しました。お疲れさまでした！")


if __name__ == "__main__":
    main()
