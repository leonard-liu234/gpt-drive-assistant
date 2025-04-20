from flask import Flask, request, jsonify, send_file, redirect
from flask_cors import CORS
from pptx import Presentation
from datetime import datetime
import os
import requests

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://gpt-drive-assistant.onrender.com/oauth2callback")
SCOPE = "https://www.googleapis.com/auth/drive.readonly"

access_tokens = {}  # 临时存储 token，可换成 session 或数据库

@app.route("/")
def home():
    return "✅ GPT Drive Assistant is running."

@app.route("/.well-known/ai-plugin.json")
def serve_manifest():
    return send_file("static/.well-known/ai-plugin.json", mimetype="application/json")

@app.route("/openapi.yaml")
def serve_openapi():
    return send_file("static/openapi.yaml", mimetype="text/yaml")

@app.route("/authorize")
def authorize():
    query = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent"
    }
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{requests.compat.urlencode(query)}")

@app.route("/oauth2callback")
def oauth2callback():
    code = request.args.get("code")
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    res = requests.post(token_url, data=data).json()
    access_tokens["user"] = res.get("access_token")
    return jsonify(res)

@app.route("/folders/<folder_id>/list", methods=["GET"])
def list_files(folder_id):
    token = access_tokens.get("user")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    headers = {"Authorization": f"Bearer {token}"}
    files = []

    def recursive_list(fid):
        params = {
            "q": f"'{fid}' in parents",
            "fields": "files(id,name,mimeType)",
            "pageSize": 1000
        }
        r = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers, params=params).json()
        for f in r.get("files", []):
            files.append(f)
            if f["mimeType"] == "application/vnd.google-apps.folder":
                recursive_list(f["id"])

    recursive_list(folder_id)
    return jsonify(files)

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)
