# DialAudioMixer+

このフォルダは Stream Deck+ 用のカスタムプラグイン `DialAudioMixer+` のスキャフォールドです。

フォルダ構成 (主要ファイル):

- `manifest.json` — プラグインのメタ情報
- `main.js` — Stream Deck 側のコード（WebSocket イベント受信）
- `plugin/` — サーバー側のユーティリティとスクリプト
  - `helper.py` — Flask を用いたローカル API（アプリ一覧、除外、音量変更エンドポイント）
  - `icon_extractor.py` — Windows exe からアイコンを抽出するヘルパー
  - `requirements.txt` — Python 依存ライブラリ
- `images/` — アイコン画像（プレースホルダが含まれます。実際の PNG を追加してください）
- `propertyinspector/` — 設定 UI (inspector.html, inspector.js, inspector.css)

セットアップ (簡易):

1. Python 依存のインストール (plugin フォルダ内で):

   pip install -r plugin\requirements.txt

2. `plugin/helper.py` を起動します:

   python plugin\helper.py

3. Stream Deck にプラグインフォルダを配置するか、デバッグ用に `main.js` を Stream Deck の開発 WebSocket と接続します。

注意:

- images/\*.png はプレースホルダになっています。実際の PNG を用意してください。
- `helper.py` の `/volume` 実装は現在ダミーです。WASAPI 等での実装が必要です。
