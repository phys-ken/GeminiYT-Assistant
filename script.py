import re
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from youtubesearchpython import Video
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import requests
from PIL import Image, ImageTk
from io import BytesIO
import os
import json
import sys

# ディレクトリとファイルのパス設定
# アプリケーションのパスを取得
if getattr(sys, 'frozen', False):
    # PyInstaller でバンドルされた場合
    application_path = os.path.dirname(sys.executable)
else:
    # 通常の Python スクリプトとして実行される場合
    application_path = os.path.dirname(os.path.abspath(__file__))

# TMP_DIR を実行ファイルと同じディレクトリに設定
TMP_DIR = os.path.join(application_path, "tmp")
API_FILE = os.path.join(TMP_DIR, "api.txt")
SETTING_FILE = os.path.join(TMP_DIR, "setting.json")
RESULT_FILE = os.path.join(TMP_DIR, "result.json")

# tmpフォルダの作成
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

# 設定のデフォルト値
default_settings = {
    "prompts": [
        "この授業動画をこれから視聴する生徒が学習の見通しを立てられるよう、はじめにキーワードを列挙し、その後で動画の内容とポイントをまとめてください。",
        "字幕を清書して、改行して結合して再表示して。",
        "この動画の内容を、教員向けに要約して、授業で使用する際のポイントや留意点も解説して。",
        "この動画の内容を要約して。"
    ]
}

# 設定の読み込み
def load_settings():
    if os.path.exists(SETTING_FILE):
        with open(SETTING_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
    else:
        settings = default_settings
        save_settings(settings)
    return settings

# 設定の保存
def save_settings(settings):
    with open(SETTING_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

# APIキーの読み込み
def load_api_key():
    if os.path.exists(API_FILE):
        with open(API_FILE, "r") as f:
            api_key = f.read().strip()
    else:
        api_key = ""
    return api_key

# APIキーの保存
def save_api_key(api_key):
    with open(API_FILE, "w") as f:
        f.write(api_key)

# 動画IDの抽出
def extract_video_id(url):
    pattern = r"(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|v/|shorts/|user/\S+/\S*/\S*|.*v=)|youtu\.be/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# 動画データの取得（日本語字幕）
def get_video_data(url):
    video_id = extract_video_id(url)
    if not video_id:
        return {"error": "無効なURLです"}

    # 標準化した動画URL
    standardized_url = f"https://www.youtube.com/watch?v={video_id}"

    # 動画情報の取得
    try:
        video_info = Video.getInfo(standardized_url)
        title = video_info.get("title", "タイトルなし")
        description = video_info.get("description", "説明なし")
        # サムネイルURLの取得
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    except Exception as e:
        return {"error": f"動画情報の取得中にエラーが発生しました: {e}"}

    # 日本語字幕の取得
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja'])
        subtitles = [entry['text'] for entry in transcript]
    except TranscriptsDisabled:
        subtitles = ["この動画では字幕が無効化されています。"]
    except NoTranscriptFound:
        subtitles = ["この動画には日本語字幕が存在しません。"]
    except Exception as e:
        subtitles = [f"字幕の取得中にエラーが発生しました: {e}"]

    # 結果を辞書形式で返す
    video_data = {
        "video_url": standardized_url,
        "title": title,
        "description": description,
        "thumbnail_url": thumbnail_url,
        "subtitles": subtitles
    }

    # result.jsonに保存
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=4)

    return video_data

# 動画データの取得（標準字幕）
def get_video_data_default(url):
    video_id = extract_video_id(url)
    if not video_id:
        return {"error": "無効なURLです"}

    # 標準化した動画URL
    standardized_url = f"https://www.youtube.com/watch?v={video_id}"

    # 動画情報の取得
    try:
        video_info = Video.getInfo(standardized_url)
        title = video_info.get("title", "タイトルなし")
        description = video_info.get("description", "説明なし")
        # サムネイルURLの取得
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    except Exception as e:
        return {"error": f"動画情報の取得中にエラーが発生しました: {e}"}

    # 標準字幕の取得
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        subtitles = [entry['text'] for entry in transcript]
    except TranscriptsDisabled:
        subtitles = ["この動画では字幕が無効化されています。"]
    except NoTranscriptFound:
        subtitles = ["この動画には字幕が存在しません。"]
    except Exception as e:
        subtitles = [f"字幕の取得中にエラーが発生しました: {e}"]

    # 結果を辞書形式で返す
    video_data = {
        "video_url": standardized_url,
        "title": title,
        "description": description,
        "thumbnail_url": thumbnail_url,
        "subtitles": subtitles
    }

    # result.jsonに保存
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=4)

    return video_data

# Gemini APIを使用してテキストを生成
def generate_with_gemini(prompt, text):
    api_key = load_api_key()
    if not api_key:
        messagebox.showerror("エラー", "APIキーが設定されていません。設定からAPIキーを入力してください。")
        return ""

    # モデル名を 'models/' を含めて設定
    model_name = "models/gemini-1.5-pro-latest"  # またはご利用可能なモデル名

    # エンドポイントURLを構築
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"

    # システムプロンプト（必要に応じて設定）
    system_prompt = ""  # 必要なら設定から取得

    # ペイロードをGASコードに合わせて構築
    payload = {
        "systemInstruction": {
            "role": "model",
            "parts": [
                {
                    "text": system_prompt
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt + "\n\n" + text
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()
        if "candidates" in response_json and len(response_json["candidates"]) > 0:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Gemini APIからの応答がありません"
    except requests.exceptions.HTTPError as e:
        error_message = response.text
        messagebox.showerror("エラー", f"Gemini APIの呼び出し中にHTTPエラーが発生しました: {e}\n詳細: {error_message}")
        return ""
    except Exception as e:
        messagebox.showerror("エラー", f"Gemini APIの呼び出し中にエラーが発生しました: {e}")
        return ""

# 「日本語字幕の取得」ボタンの処理
def on_fetch():
    url = url_entry.get()
    result = get_video_data(url)
    if "error" in result:
        messagebox.showerror("エラー", result["error"])
        return

    # 動画情報の表示
    title_label.config(text=result["title"])
    description_text.config(state=tk.NORMAL)
    description_text.delete('1.0', tk.END)
    description_text.insert(tk.END, result["description"])
    description_text.config(state=tk.DISABLED)

    # サムネイル画像の表示
    try:
        response = requests.get(result["thumbnail_url"])
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((320, 180))  # サイズ調整
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo  # 参照を保持
    except Exception:
        # サムネイルが取得できない場合はデフォルト画像を表示
        image_label.config(image=default_photo)
        image_label.image = default_photo

    # 字幕の表示
    subtitles_text.config(state=tk.NORMAL)
    subtitles_text.delete('1.0', tk.END)
    subtitles_text.insert(tk.END, "\n".join(result["subtitles"]))
    subtitles_text.config(state=tk.NORMAL)  # 編集可能にする

    # 「字幕を一括コピー」ボタンを有効化
    copy_all_button.config(state=tk.NORMAL)

    # プロンプトのリフレッシュ
    refresh_prompts()

    # 「Geminiに送信」ボタンを有効化
    send_button.config(state=tk.NORMAL)

# 「標準字幕の取得」ボタンの処理
def on_fetch_default():
    url = url_entry.get()
    result = get_video_data_default(url)
    if "error" in result:
        messagebox.showerror("エラー", result["error"])
        return

    # 動画情報の表示
    title_label.config(text=result["title"])
    description_text.config(state=tk.NORMAL)
    description_text.delete('1.0', tk.END)
    description_text.insert(tk.END, result["description"])
    description_text.config(state=tk.DISABLED)

    # サムネイル画像の表示
    try:
        response = requests.get(result["thumbnail_url"])
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((320, 180))  # サイズ調整
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo  # 参照を保持
    except Exception:
        # サムネイルが取得できない場合はデフォルト画像を表示
        image_label.config(image=default_photo)
        image_label.image = default_photo

    # 字幕の表示
    subtitles_text.config(state=tk.NORMAL)
    subtitles_text.delete('1.0', tk.END)
    subtitles_text.insert(tk.END, "\n".join(result["subtitles"]))
    subtitles_text.config(state=tk.NORMAL)  # 編集可能にする

    # 「字幕を一括コピー」ボタンを有効化
    copy_all_button.config(state=tk.NORMAL)

    # プロンプトのリフレッシュ
    refresh_prompts()

    # 「Geminiに送信」ボタンを有効化
    send_button.config(state=tk.NORMAL)

# 字幕を一括コピー
def copy_all_subtitles():
    subtitles = subtitles_text.get('1.0', tk.END).strip()
    root.clipboard_clear()
    root.clipboard_append(subtitles)
    # 一時的なメッセージを表示
    message_label.config(text="全ての字幕をクリップボードにコピーしました")
    root.after(2000, lambda: message_label.config(text=""))  # 2秒後にメッセージを消す

# Geminiに送信
def send_to_gemini():
    prompt_index = prompt_combobox.current()
    if prompt_index == -1:
        messagebox.showwarning("警告", "プロンプトが選択されていません。")
        return

    prompt = settings["prompts"][prompt_index]

    subtitles = subtitles_text.get('1.0', tk.END).strip()
    if not subtitles:
        messagebox.showwarning("警告", "字幕がありません。")
        return

    # Gemini APIを呼び出し、結果を表示
    gemini_text.config(state=tk.NORMAL)
    gemini_text.delete('1.0', tk.END)
    response = generate_with_gemini(prompt, subtitles)
    gemini_text.insert(tk.END, response)
    gemini_text.config(state=tk.NORMAL)

    # 最後の応答を保存
    global last_response
    last_response = response

    # 「Geminiの応答をコピー」ボタンを有効化
    copy_gemini_button.config(state=tk.NORMAL)

# Geminiの応答をコピー
def copy_gemini_response():
    root.clipboard_clear()
    root.clipboard_append(last_response)
    # 一時的なメッセージを表示
    message_label.config(text="Geminiの応答をクリップボードにコピーしました")
    root.after(2000, lambda: message_label.config(text=""))

# 設定画面の表示
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("設定")
    settings_window.geometry("600x500")

    # APIキーの設定
    ttk.Label(settings_window, text="Gemini APIキー:").pack(anchor="w", padx=10, pady=5)
    api_key_entry = ttk.Entry(settings_window, width=60, show="*")
    api_key_entry.pack(padx=10, pady=5)
    api_key_entry.insert(0, load_api_key())

    # プロンプトの設定
    ttk.Label(settings_window, text="プロンプトの設定:").pack(anchor="w", padx=10, pady=5)
    prompt_frame = ttk.Frame(settings_window)
    prompt_frame.pack(fill="both", expand=True, padx=10, pady=5)

    prompt_entries = []

    def add_prompt_entry(prompt_text=""):
        entry_frame = ttk.Frame(prompt_frame)
        entry_frame.pack(fill="x", pady=5)
        prompt_entry = scrolledtext.ScrolledText(entry_frame, wrap=tk.WORD, height=4)
        prompt_entry.pack(side="left", fill="x", expand=True)
        prompt_entry.insert(tk.END, prompt_text)
        remove_button = ttk.Button(entry_frame, text="－", command=lambda: remove_prompt_entry(entry_frame))
        remove_button.pack(side="left", padx=5)
        prompt_entries.append((prompt_entry, entry_frame))

    def remove_prompt_entry(entry_frame):
        for i, (entry, frame) in enumerate(prompt_entries):
            if frame == entry_frame:
                prompt_entries.pop(i)
                entry_frame.destroy()
                break

    # 既存のプロンプトをロード
    for prompt_text in settings["prompts"]:
        add_prompt_entry(prompt_text)

    # プロンプト追加ボタン
    add_prompt_button = ttk.Button(settings_window, text="＋", command=add_prompt_entry)
    add_prompt_button.pack(pady=5)

    # 設定の保存
    def save_settings_action():
        new_api_key = api_key_entry.get().strip()
        save_api_key(new_api_key)

        new_prompts = [entry.get('1.0', tk.END).strip() for entry, frame in prompt_entries if entry.get('1.0', tk.END).strip()]
        settings["prompts"] = new_prompts
        save_settings(settings)

        messagebox.showinfo("情報", "設定を保存しました。")
        settings_window.destroy()
        refresh_prompts()

    save_button = ttk.Button(settings_window, text="保存", command=save_settings_action)
    save_button.pack(pady=10)

# プロンプトのリフレッシュ
def refresh_prompts():
    prompts = settings["prompts"]
    if prompts:
        display_prompts = [prompt if len(prompt) <= 50 else prompt[:47] + '...' for prompt in prompts]
        prompt_combobox['values'] = display_prompts
        prompt_combobox.current(0)
    else:
        prompt_combobox['values'] = ['']
        prompt_combobox.set('')
        send_button.config(state=tk.DISABLED)

# メインウィンドウの作成
root = tk.Tk()
root.title("YouTube字幕取得アプリ")
root.geometry("800x800")

# スタイルの設定
style = ttk.Style()
style.theme_use('clam')  # 現代風なテーマを使用

# メインフレーム
main_frame = ttk.Frame(root, padding=10)
main_frame.grid(row=0, column=0, sticky="nsew")

# 行と列の設定
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=0)
main_frame.rowconfigure(7, weight=1)  # 字幕テキストエリアの行
main_frame.rowconfigure(9, weight=1)  # Geminiの応答エリア

# メニューの作成
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
menu_bar.add_command(label="設定", command=open_settings)

# 設定の読み込み
settings = load_settings()

# URL入力欄
url_label = ttk.Label(main_frame, text="YouTubeのURLを入力してください:")
url_label.grid(row=0, column=0, sticky="w")
url_entry = ttk.Entry(main_frame, width=50)
url_entry.grid(row=1, column=0, sticky="ew", pady=5)

# ボタンフレームの作成
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=1, column=1, sticky="e", padx=5)

# 「日本語字幕の取得」ボタン
fetch_button = ttk.Button(button_frame, text="日本語字幕の取得", command=on_fetch)
fetch_button.pack(side='left', padx=5)

# 「標準字幕の取得」ボタン
fetch_default_button = ttk.Button(button_frame, text="標準字幕の取得", command=on_fetch_default)
fetch_default_button.pack(side='left', padx=5)

# メッセージラベル
message_label = ttk.Label(main_frame, text="", foreground="green")
message_label.grid(row=2, column=0, columnspan=2, sticky="w")

# 動画情報フレーム
info_frame = ttk.Frame(main_frame)
info_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=10)
info_frame.columnconfigure(1, weight=1)
info_frame.rowconfigure(1, weight=1)

# デフォルトのサムネイル画像をロード
try:
    default_img = Image.open("default_thumbnail.png")
except FileNotFoundError:
    default_img = Image.new("RGB", (320, 180), color="#CCCCCC")
default_img = default_img.resize((320, 180))
default_photo = ImageTk.PhotoImage(default_img)

# サムネイル画像の表示
image_label = ttk.Label(info_frame, image=default_photo)
image_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5)

# タイトル表示
title_label = ttk.Label(info_frame, text="動画のタイトルがここに表示されます", font=("Helvetica", 16, "bold"), wraplength=400, anchor="w")
title_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)

# 概要欄の表示
description_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, height=5)
description_text.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
description_text.insert(tk.END, "動画の概要欄がここに表示されます。")
description_text.config(state=tk.DISABLED)

# 区切り線
separator = ttk.Separator(main_frame, orient='horizontal')
separator.grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

# プロンプト選択フレーム
prompts_frame = ttk.LabelFrame(main_frame, text="プロンプトの選択")
prompts_frame.grid(row=5, column=0, columnspan=2, sticky="ew")

selected_prompt = tk.StringVar()
prompt_combobox = ttk.Combobox(prompts_frame, textvariable=selected_prompt, state="readonly")
prompt_combobox.pack(fill="x", padx=10, pady=5)

refresh_prompts()

# Geminiに送信ボタン
send_button = ttk.Button(main_frame, text="Geminiに送信", command=send_to_gemini, state=tk.DISABLED)
send_button.grid(row=6, column=0, columnspan=2, pady=5)

# 字幕フレーム
subtitles_frame = ttk.LabelFrame(main_frame, text="字幕")
subtitles_frame.grid(row=7, column=0, columnspan=2, sticky="nsew")
subtitles_frame.columnconfigure(0, weight=1)
subtitles_frame.rowconfigure(0, weight=1)

# 字幕のテキストボックス
subtitles_text = scrolledtext.ScrolledText(subtitles_frame, wrap=tk.WORD)
subtitles_text.grid(row=0, column=0, sticky="nsew")
subtitles_text.insert(tk.END, "動画の字幕がここに表示されます。")
subtitles_text.config(state=tk.DISABLED)  # 初期状態は編集不可

# 「字幕を一括コピー」ボタン
copy_all_button = ttk.Button(main_frame, text="字幕を一括コピー", command=copy_all_subtitles, state=tk.DISABLED)
copy_all_button.grid(row=8, column=0, columnspan=2, pady=5)

# Geminiの応答フレーム
gemini_frame = ttk.LabelFrame(main_frame, text="Geminiの応答")
gemini_frame.grid(row=9, column=0, columnspan=2, sticky="nsew", pady=10)
gemini_frame.columnconfigure(0, weight=1)
gemini_frame.rowconfigure(0, weight=1)

# Geminiの応答テキストボックス
gemini_text = scrolledtext.ScrolledText(gemini_frame, wrap=tk.WORD)
gemini_text.grid(row=0, column=0, sticky="nsew")
gemini_text.config(state=tk.NORMAL)  # 編集可能にする

# 「Geminiの応答をコピー」ボタン
copy_gemini_button = ttk.Button(main_frame, text="Geminiの応答をコピー", command=copy_gemini_response, state=tk.DISABLED)
copy_gemini_button.grid(row=10, column=0, columnspan=2, pady=5)

# ウィンドウの行と列の設定
main_frame.rowconfigure(7, weight=1)  # 字幕テキストエリアが余分なスペースを占有
main_frame.rowconfigure(9, weight=1)  # Geminiの応答エリア
main_frame.columnconfigure(0, weight=1)

# 最後の応答を保存する変数
last_response = ""

# アプリケーションの実行
root.mainloop()
