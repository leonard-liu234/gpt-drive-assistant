from flask import Flask, request, jsonify, send_file
import os
import requests
from pptx import Presentation
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

@app.route("/", methods=["GET"])
def health_check():
    return "✅ GPT Drive Assistant is running"

@app.route("/.well-known/ai-plugin.json", methods=["GET"])
def plugin_manifest():
    return send_file("static/.well-known/ai-plugin.json", mimetype="application/json")

@app.route("/openapi.yaml", methods=["GET"])
def openapi_spec():
    return send_file("static/openapi.yaml", mimetype="text/yaml")

@app.route("/logo.png", methods=["GET"])
def serve_logo():
    return send_file("static/logo.png", mimetype="image/png")

@app.route("/legal", methods=["GET"])
def legal():
    return "Legal information placeholder."

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

@app.route("/folders/<folder_id>/list", methods=["GET"])
def list_drive_files(folder_id):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    all_files = []

    def fetch_folder_contents(fid):
        params = {
            "q": f"'{fid}' in parents and trashed = false",
            "fields": "files(id,name,mimeType)",
            "pageSize": 1000
        }
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers, params=params)
        if res.status_code == 200:
            files = res.json().get("files", [])
            for f in files:
                all_files.append(f)
                if f["mimeType"] == "application/vnd.google-apps.folder":
                    fetch_folder_contents(f["id"])
        else:
            raise Exception(res.text)

    try:
        fetch_folder_contents(folder_id)
        return jsonify(all_files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "199234xxx")
    app.run(host="0.0.0.0", port=5000)
