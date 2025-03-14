import requests
from flask import Flask, request, jsonify
from PyPDF2 import PdfMerger
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ PDF Merge API が実行されています!"

# 📌 `POST` メソッドを許可し、PDFをダウンロードしてマージ
@app.route("/merge_pdfs", methods=["POST"])
def merge_pdfs():
    try:
        pdf_urls = request.json.get("pdf_files", [])  # JSONデータを取得
        output_file = "/tmp/merged_output.pdf"  # Renderの一時保存フォルダ

        if not pdf_urls:
            return jsonify({"error": "PDFファイルのURLが指定されていません"}), 400

        # 📌 PDFの一時保存フォルダ
        temp_pdf_files = []

        # 📌 各PDFをダウンロードし、一時ファイルとして保存
        for i, pdf_url in enumerate(pdf_urls):
            response = requests.get(pdf_url)
            if response.status_code != 200:
                return jsonify({"error": f"ダウンロード失敗: {pdf_url}"}), 400

            temp_path = f"/tmp/temp_pdf_{i}.pdf"
            with open(temp_path, "wb") as f:
                f.write(response.content)

            temp_pdf_files.append(temp_path)

        # 📌 PDFをマージ
        merger = PdfMerger()
        for pdf in temp_pdf_files:
            merger.append(pdf)
        merger.write(output_file)
        merger.close()

        # 📌 一時ファイルを削除
        for pdf in temp_pdf_files:
            os.remove(pdf)

        return jsonify({"message": "✅ PDFマージ完了", "output_file": output_file})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
