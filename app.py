from flask import Flask, request, jsonify, send_file
from pptx import Presentation
from pptx.util import Inches
import os
import requests
from datetime import datetime

app = Flask(__name__)
ACCESS_TOKEN = os.getenv("GDRIVE_ACCESS_TOKEN")

@app.route("/generate-ppt", methods=["POST"])
def generate_ppt():
    data = request.get_json()
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    body = slide.placeholders[1]
    title.text = "确认函摘要"
    body.text = (
        f"项目名称：{data.get('project_name')}\n"
        f"客户名称：{data.get('client_name')}\n"
        f"联系方式：{data.get('contact')}\n"
        f"报价编号：{data.get('quote_number')}\n"
        f"报价日期：{data.get('quote_date')}"
    )
    os.makedirs("generated_ppt", exist_ok=True)
    filename = f"confirmation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
    filepath = os.path.join("generated_ppt", filename)
    prs.save(filepath)
    return jsonify({"download_url": f"/download-ppt/{filename}"})


@app.route("/download-ppt/<filename>", methods=["GET"])
def download_ppt(filename):
    return send_file(os.path.join("generated_ppt", filename), as_attachment=True)


@app.route("/folders/<folder_id>/list", methods=["GET"])
def list_folder_files(folder_id):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    params = {
        "q": f"'{folder_id}' in parents",
        "fields": "files(id,name,mimeType)",
        "pageSize": 100
    }
    response = requests.get("https://www.googleapis.com/drive/v3/files", headers=headers, params=params)
    if response.status_code != 200:
        return jsonify({"error": response.text}), response.status_code
    return jsonify(response.json().get("files", []))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
