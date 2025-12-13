import psutil
import json
from flask import Flask, request, jsonify
from icon_extractor import extract_icon
import os
import base64
import tempfile
import logging

# pycaw（Windows用オーディオ制御）インポート試行
try:
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    from comtypes import CLSCTX_ALL
    PYCAW_AVAILABLE = True
except Exception:
    PYCAW_AVAILABLE = False

# =======================
# Flask アプリ初期化
# =======================
app = Flask(__name__)

# Flask/Werkzeugのアクセスログを非表示（HTTP GET/POST行を抑制）
logging.getLogger('werkzeug').setLevel(logging.ERROR)
app.logger.disabled = True

EXCLUDE_FILE = "exclude.json"

# 初期化: 除外リストファイルが無ければ作成
if not os.path.exists(EXCLUDE_FILE):
    with open(EXCLUDE_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# =======================
# 除外リスト読み込み/保存
# =======================
def load_excluded():
    """除外リストを読み込む"""
    with open(EXCLUDE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_excluded(lst):
    """除外リストを保存"""
    with open(EXCLUDE_FILE, "w", encoding="utf-8") as f:
        json.dump(lst, f, indent=2)

# =======================
# /apps : 音声セッションのあるアプリ一覧取得
# =======================
@app.get("/apps")
def list_audio_apps():
    """アクティブ音声セッションのあるプロセス一覧を返す"""
    excluded = load_excluded()
    result = []
    seen_names = set()
    
    if PYCAW_AVAILABLE:
        # pycawが利用可能な場合、音声セッションからPIDを取得
        try:
            sessions = AudioUtilities.GetAllSessions()
            
            for session in sessions:
                try:
                    ctl = session._ctl
                    guid = str(ctl.GetGroupingParam())
                    p = psutil.Process(session.Process.pid)
                    name, ext = os.path.splitext(session.Process.name())  # ext = ".exe", name = "Discord"

                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    try:
                        current = volume.GetMasterVolume()
                    except Exception:
                        current = 0.0
                    final_volume = min(1.0, max(0.0, current + (0 / 100.0)))
                    print(f"[/apps] PID={session.Process.pid}, Name={name}, GUID={guid}, Volume={final_volume}" )
                    if name not in excluded and name not in seen_names:
                        result.append({"pid": session.Process.pid,"guid": guid, "name": name, "volume": final_volume})
                        seen_names.add(name)
                except Exception:
                    pass
        except Exception as e:
            print(f"[/apps] ERROR: {e}")
    else:
        # pycawが利用できない場合は全プロセスを返す（重複除去）
        for p in psutil.process_iter(["pid", "name"]):
            name = p.info["name"]
            if name not in excluded and name not in seen_names:
                result.append({"pid": p.info["pid"], "name": name})
                seen_names.add(name)

    return jsonify(result)


# =======================
# /exclude : アプリ名を除外リストに追加
# =======================
@app.get("/exclude")
def add_exclude():
    name = request.args.get("name")
    if not name:
        return jsonify({"status": "error", "message": "missing name"}), 400
    excluded = load_excluded()
    if name not in excluded:
        excluded.append(name)
        save_excluded(excluded)
    return jsonify({"status": "ok"})

# =======================
# /unexclude : アプリ名を除外リストから削除
# =======================
@app.get("/unexclude")
def remove_exclude():
    name = request.args.get("name")
    if not name:
        return jsonify({"status": "error", "message": "missing name"}), 400
    excluded = load_excluded()
    if name in excluded:
        excluded.remove(name)
        save_excluded(excluded)
    return jsonify({"status": "ok"})


# =======================
# /volume_set : 絶対値で音量設定
# =======================
@app.get("/volume_set")
def set_volume_absolute():
    if not PYCAW_AVAILABLE:
        return jsonify({"status": "error", "message": "pycaw not installed"}), 500
    
    name_arg = request.args.get("name")
    vol_arg = request.args.get("vol")
    try:
        vol = float(vol_arg)
    except Exception:
        return jsonify({"status": "error", "message": "invalid pid or vol"}), 400

    vol = min(1.0, max(0.0, vol))
    sessions = AudioUtilities.GetAllSessions()

    for session in sessions:
        try:
            ctl = session._ctl
            name, ext = os.path.splitext(session.Process.name()) 
        except Exception:
            continue
        if name == name_arg:
            volctl = ctl.QueryInterface(ISimpleAudioVolume)
            volctl.SetMasterVolume(vol, None)

    return jsonify({"status": "ok", "volume": vol})

# =======================
# /_log : デバッグログ受信
# =======================
@app.get("/_log")
def receive_log():
    m = request.args.get("m")
    try:
        print(f"[main.js] {m}")
    except Exception:
        print("[main.js] <unprintable message>")
    return jsonify({"status": "ok"})

# =======================
# /icon : プロセスのアイコン取得
# =======================
@app.get('/icon')
def get_icon():
    pid_arg = request.args.get('pid')
    if not pid_arg:
        return jsonify({"status": "error", "message": "missing pid"}), 400
    try:
        pid = int(pid_arg)
    except Exception:
        return jsonify({"status": "error", "message": "invalid pid"}), 400

    try:
        p = psutil.Process(pid)
        exe_path = p.exe()
    except Exception as e:
        print(f"[/icon] process lookup error: {e}")
        return jsonify({"status": "error", "message": "process not found"}), 404

    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        tmp.close()
        ok = extract_icon(exe_path, tmp.name)
        if not ok:
            try: os.remove(tmp.name)
            except Exception: pass
            return jsonify({"status": "error", "message": "icon extraction failed"}), 500
        with open(tmp.name, 'rb') as f:
            b = f.read()
        data_url = 'data:image/png;base64,' + base64.b64encode(b).decode('ascii')

        try: os.remove(tmp.name)
        except Exception: pass
        return jsonify({"status": "ok", "data_url": data_url})
    except Exception as e:
        print(f"[/icon] ERROR: {e}")
        if tmp:
            try: os.remove(tmp.name)
            except Exception: pass
        return jsonify({"status": "error", "message": str(e)}), 500

# =======================
# メイン実行
# =======================
if __name__ == "__main__":
    app.run(port=8823)
