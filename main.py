import os
import time
import csv
import random
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


def load_played_words(filename):
    """
    record.csvから既に再生済みの単語リストを読み込む

    Args:
        filename (str): record.csvファイルのパス

    Returns:
        set: 再生済み単語のセット
    """
    played_words = set()
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # ヘッダーをスキップ
            for row in csv_reader:
                if row:  # 空行でない場合
                    played_words.add(row[0].strip())
    except FileNotFoundError:
        # ファイルが存在しない場合は空のセットを返す
        pass
    except Exception as e:
        print(f"record.csv読み込みエラー: {e}")

    return played_words


def save_played_word(filename, word):
    """
    再生した単語をrecord.csvに保存する

    Args:
        filename (str): record.csvファイルのパス
        word (str): 再生した英単語
    """
    file_exists = os.path.exists(filename)

    try:
        with open(filename, 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['english'])  # ヘッダーを書き込み
            writer.writerow([word])
    except Exception as e:
        print(f"record.csv書き込みエラー: {e}")


def ask_random_mode():
    """
    ランダムモードを使用するかユーザーに確認する

    Returns:
        bool: ランダムモードを使用する場合True
    """
    while True:
        print("\n単語をランダムに表示しますか？")
        print("y: ランダム表示（重複なし）")
        print("n: 順番通り表示")
        choice = input("選択してください (y/n): ").lower().strip()

        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print("yまたはnを入力してください。")


def check_record_file_overwrite():
    """
    record.csvが既に存在する場合、上書きするか確認する

    Returns:
        bool: 上書きする場合True、しない場合False
    """
    record_filename = "record.csv"
    if os.path.exists(record_filename):
        while True:
            print(f"\n{record_filename}が既に存在します。")
            print("このファイルには過去に再生した単語の記録が保存されています。")
            choice = input("上書きしてもよろしいですか？ (y/n): ").lower().strip()

            if choice == 'y':
                try:
                    os.remove(record_filename)
                    print("record.csvを削除しました。新しい記録を開始します。")
                    return True
                except Exception as e:
                    print(f"ファイル削除エラー: {e}")
                    return False
            elif choice == 'n':
                print("既存の記録を継続します。")
                return False
            else:
                print("yまたはnを入力してください。")
    return True


def get_target_word_count(total_words, available_words=None):
    """
    今日再生する単語数を入力で取得する

    Args:
        total_words (int): CSVファイル内の総単語数
        available_words (int): 再生可能な単語数（ランダムモードの場合）

    Returns:
        int: 今日再生する単語数
    """
    while True:
        try:
            print(f"\nCSVファイル内の総単語数: {total_words}語")
            if available_words is not None and available_words < total_words:
                print(f"再生可能な単語数（未再生）: {available_words}語")
                max_words = available_words
            else:
                max_words = total_words

            if max_words == 0:
                print("再生可能な単語がありません。record.csvを削除してやり直してください。")
                return 0

            target_count = int(input("今日再生する単語数を入力してください: "))

            if target_count <= 0:
                print("1以上の数値を入力してください。")
                continue
            elif target_count > max_words:
                print(f"入力された数値が再生可能な単語数({max_words}語)を超えています。")
                print(f"最大{max_words}語まで設定できます。")
                continue
            else:
                return target_count
        except ValueError:
            print("有効な数値を入力してください。")


def play_words(word_data, target_count, random_mode=False):
    """
    辞書リストから英単語を順番に3回ずつ再生する
    3回目の再生時に日本語を表示
    指定した単語数に達したらストップ

    Args:
        word_data (list): [{'english': '英単語', 'japanese': '日本語'}, ...] の辞書リスト
        target_count (int): 今日再生する単語数
        random_mode (bool): ランダムモードかどうか
    """
    if target_count == 0:
        return

    # pygameの初期化
    pygame.mixer.init()

    # 一時ディレクトリを作成
    temp_dir = tempfile.mkdtemp()
    record_filename = "record.csv"

    try:
        played_count = 0

        # ランダムモードの場合はデータをシャッフル
        if random_mode:
            word_data = word_data.copy()  # 元のリストを変更しないようにコピー
            random.shuffle(word_data)

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
            temp_file = os.path.join(
                temp_dir, f"{english_word.replace('/', '_')}.mp3")
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

            # ランダムモードの場合は再生した単語を記録
            if random_mode:
                save_played_word(record_filename, english_word)

            # 次の単語との間隔
            time.sleep(0.7)

            # 一時ファイルを削除
            if os.path.exists(temp_file):
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

    # ランダムモードを使用するか確認
    random_mode = ask_random_mode()

    if random_mode:
        # record.csvの上書き確認
        overwrite_record = check_record_file_overwrite()

        if overwrite_record:
            # 新しい記録を開始
            available_words = total_words
            target_words = word_data
        else:
            # 既存の記録を使用
            played_words = load_played_words("record.csv")
            target_words = [
                word for word in word_data if word['english'] not in played_words]
            available_words = len(target_words)

            print(f"既に再生済みの単語数: {len(played_words)}語")

        # 今日再生する単語数を取得
        target_count = get_target_word_count(total_words, available_words)
        word_data_to_play = target_words
    else:
        # 順番モード
        target_count = get_target_word_count(total_words)
        word_data_to_play = word_data

    if target_count > 0:
        print("\n" + "-" * 60)
        print("英単語の音声再生を開始します...")
        print("各単語を3回ずつ再生し、3回目の再生時に日本語を表示します。")
        print("単語間に0.7秒の間隔をあけます。")
        print(f"モード: {'ランダム表示' if random_mode else '順番表示'}")
        print(f"今日の目標: {target_count}語")
        print("-" * 60)

        play_words(word_data_to_play, target_count, random_mode)

    print("-" * 60)
    print("プログラムを終了しました。お疲れさまでした！")


if __name__ == "__main__":
    main()
