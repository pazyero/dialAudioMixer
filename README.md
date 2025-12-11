# DialAudioMixer for Stream Deck

## 概要
**DialAudioMixer** は、Elgato Stream Deck 用のプラグインで、Windows上のアクティブなオーディオアプリを管理し、ダイヤル操作で個別アプリの音量を調整できるプラグインです。

- Stream Deck のダイヤル（エンコーダー）で音量操作
- アクティブなアプリを自動検出
- アイコンと音量をStream Deck上に表示
- アプリの除外リスト機能
- 音量の増減・絶対設定対応

---

## 動作環境
- Windows 10 / 11
- Stream Deck 5.0 以上
- Python 3.8 以上

### Python 依存パッケージ
- psutil
- pycaw
- comtypes
- Pillow
- Flask
- pywin32

---

## インストール方法

1. このリポジトリをダウンロードまたはクローン
2. `DialAudioMixer.streamDeckPlugin` フォルダを作成（同梱は後々作成予定）
3. フォルダを `.zip` に圧縮し、拡張子を `.streamDeckPlugin` に変更
4. ダブルクリックして Stream Deck にインストール

---

## 使い方

1. Stream Deck 上で「Dial Audio Mixer」アクションを追加
2. アクションのダイヤルを回すとアクティブなアプリの音量が変更されます
3. アプリ名と音量がダイヤル上に表示されます
4. 除外したいアプリはプラグイン設定から追加可能

---

## 開発用

- プラグインJS/WebSocket: `Actions/DialAudioMixer/main.js`
- Pythonサーバ: `helper.py`
- アイコン抽出: `icon_extractor.py`

### 起動
Pythonサーバを手動で起動する場合:

```bash
cd python_server
pip install -r requirements.txt
python helper.py
