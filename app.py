from flask import Flask, request, jsonify, send_file, redirect, session
from flask_cors import CORS
from pptx import Presentation
import os
import requests
from datetime import datetime
from urllib.parse import urlencode

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# 配置环境变量
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://gpt-drive-assistant.onrender.com/oauth2callback")
ACCESS_TOKEN = os.getenv("GDRIVE_ACCESS_TOKEN")  # fallback 授权用

app.secret_key = os.getenv("FLASK_SECRET_KEY", "199234xxx")

@app.route("/", methods=["GET"])
def index():
    return "✅ GPT Drive Assistant is running. Use /generate-ppt or /folders/<folder_id>/list to start."

@app.route("/.well-known/ai-plugin.json", methods=["GET"])
def plugin_manifest():
    return send_file("static/.well-known/ai-plugin.json", mimetype="application/json")

@app.route("/openapi.yaml", methods=["GET"])
def openapi_spec():
    return send_file("static/openapi.yaml", mimetype="text/yaml")

@app.route("/logo.png", methods=["GET"])
def plugin_logo():
    return send_file("static/logo.png", mimetype="image/png")

@app.route("/generate-ppt", methods=["POST"])
def generate_ppt():
    data = request.get_json()
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    body = slide.placeholders[1]
    title.text = "确认函摘要"
    body.text = f"""项目名称：{data.get('project_name')}
客户名称：{data.get('client_name')}
联系方式：{data.get('contact')}
报价编号：{data.get('quote_number')}
报价日期：{data.get('quote_date')}"""
    os.makedirs("generated_ppt", exist_ok=True)
    filename = f"confirmation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
    filepath = os.path.join("generated_ppt", filename)
    prs.save(filepath)
    return jsonify({"download_url": f"/download-ppt/{filename}"})

@app.route("/download-ppt/<filename>", methods=["GET"])
def download_ppt(filename):
    return send_file(os.path.join("generated_ppt", filename), as_attachment=True)

def list_drive_files(folder_id, headers, recursive=True, collected=None):
    if collected is None:
        collected = []
    params = {
        "q": f"'{folder_id}' in parents",
        "fields": "files(id,name,mimeType)",
        "pageSize": 1000
    }
    response = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers, params=params)
    if response.status_code != 200:
        return collected
    files = response.json().get("files", [])
    for f in files:
        collected.append(f)
        if recursive and f["mimeType"] == "application/vnd.google-apps.folder":
            list_drive_files(f["id"], headers, recursive, collected)
    return collected

@app.route("/folders/<folder_id>/list", methods=["GET"])
def list_folder_files(folder_id):
    access_token = session.get("access_token") or ACCESS_TOKEN
    if not access_token:
        return jsonify({"error": "Missing Google Drive access token"}), 403
    headers = {"Authorization": f"Bearer {access_token}"}
    all_files = list_drive_files(folder_id, headers)
    return jsonify(all_files)

@app.route("/authorize")
def authorize():
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/drive.readonly",
        "redirect_uri": REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent"
    })
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{query}")

@app.route("/oauth2callback")
def oauth2callback():
    code = request.args.get("code")
    if not code:
        return "No code provided", 400
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=data)
    token_data = response.json()
    session["access_token"] = token_data.get("access_token")
    session["refresh_token"] = token_data.get("refresh_token")
    return jsonify(token_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
