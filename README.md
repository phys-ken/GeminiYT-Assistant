# YouTube字幕取得＆Gemini API連携ツール

https://github.com/user-attachments/assets/5a998fda-ebda-4cba-90db-0a3bc8a1f6c1

以下のREADMEは生成AIで作成しました(後日修正予定です)

## 概要

このツールは、YouTube動画の日本語字幕を簡単に取得し、さらにGemini APIを活用して字幕内容をもとにしたテキスト生成を行える多機能アプリケーションです。教育者やコンテンツ制作者向けに設計されており、動画の字幕を活用して解説や要約、キーワード抽出などを行いたい場合に便利です。

## できること

- **YouTube字幕の自動取得**  
  YouTubeのURLを入力するだけで、対応する動画の日本語字幕を自動的に取得します。字幕が無効化されている場合もエラーをわかりやすく表示するため、対応状況をすぐに把握できます。

- **字幕の一括コピー**  
  取得した字幕をワンクリックでクリップボードにコピーでき、別のアプリケーションへ簡単に貼り付けることができます。

- **Gemini APIによるテキスト生成**  
  字幕の内容を基にして、あらかじめ設定したプロンプトに応じたテキスト生成を行います。例えば、動画の要約や視聴者へのキーワード紹介、教員向けのポイント解説など、用途に応じたテキスト生成が可能です。

- **カスタマイズ可能なプロンプト設定**  
  Gemini APIに送信するプロンプトを設定画面から追加・編集でき、状況に応じたプロンプトを保存して簡単に切り替えることができます。

## 主な利用メリット

1. **効率的な字幕取得とテキスト生成**  
   手動で字幕を確認し、テキストに落とし込む作業を自動化することで、コンテンツ制作や授業準備の効率を大幅に向上できます。

2. **簡単操作で多機能な活用**  
   シンプルな操作画面でありながら、テキスト生成のカスタマイズ性も備えているため、誰でもすぐに使い始められます。生成されたテキストはすぐにクリップボードにコピーでき、資料作成やSNS投稿などにも活用しやすいです。

3. **幅広い応用性**  
   教育、プレゼンテーション、コンテンツ制作、要約の自動生成など、さまざまな場面で役立つ機能を提供しています。Gemini APIと組み合わせることで、機械学習による高度なテキスト生成を手軽に体験できます。

## 技術について

このアプリケーションは、以下の技術を使用して構築されています。

- **Python**: メインのプログラミング言語
- **Tkinter**: ユーザーインターフェースの構築
- **YouTube Transcript ライブラリ**: YouTube字幕の取得
- **Gemini API**: 生成AIによるテキスト生成
- **PyInstaller**: Pythonスクリプトを実行ファイルに変換

アプリはYouTube Transcript APIおよびGemini APIと連携して動作します。PyInstallerを使用して1つの実行ファイルにまとめており、ユーザーはPython環境を意識せずにアプリケーションを利用できます。
