from flask import Flask, request, jsonify
from PyPDF2 import PdfMerger
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "PDF Merge API is running!"

# 📌 PDFを結合するエンドポイント（POSTリクエストを受け付ける）
@app.route("/merge_pdfs", methods=["POST"])
def merge_pdfs():
    try:
        pdf_files = request.json.get("pdf_files", [])  # JSONのリクエストデータを取得
        output_file = "/tmp/merged_output.pdf"  # Renderの一時保存用フォルダ

        if not pdf_files:
            return jsonify({"error": "PDFファイルが指定されていません"}), 400

        # 📌 PDFをマージ
        merger = PdfMerger()
        for pdf_url in pdf_files:
            merger.append(pdf_url)
        merger.write(output_file)
        merger.close()

        return jsonify({"message": "✅ PDFマージ完了", "output_file": output_file})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
