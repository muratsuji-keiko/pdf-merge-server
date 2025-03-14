import requests
import time
import traceback
import os
import re
import base64
from flask import Flask, request, jsonify
from PyPDF2 import PdfMerger

app = Flask(__name__)

# 🚀 ファイル名をサニタイズする関数
def sanitize_filename(filename):
    return re.sub(r'[\\/:*?"<>|]', '_', filename)

@app.route("/", methods=["GET"])
def home():
    return "✅ PDF Merge API が実行されています!"

# 📌 追加: GASからBase64エンコードされたPDFを受け取るエンドポイント
@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    try:
        data = request.json
        filename = data.get("filename")
        file_content = data.get("data")

        if not filename or not file_content:
            return jsonify({"error": "ファイル名またはデータが不足しています"}), 400

        # 🚀 Base64デコード処理
        try:
            pdf_data = base64.b64decode(file_content)
        except Exception as e:
            return jsonify({"error": f"Base64デコードエラー: {str(e)}"}), 400

        # ファイル名をサニタイズ
        sanitized_filename = sanitize_filename(filename)
        output_path = f"/tmp/{sanitized_filename}"

        with open(output_path, "wb") as f:
            f.write(pdf_data)

        print(f"✅ PDF受信完了: {output_path}")

        return jsonify({"message": "✅ PDFアップロード成功", "saved_file": output_path}), 200

    except Exception as e:
        error_message = traceback.format_exc()
        print(f"❌ エラー:\n{error_message}")
        return jsonify({"error": str(e)}), 500

@app.route("/merge_pdfs", methods=["POST"])
def merge_pdfs():
    start_time = time.time()
    try:
        pdf_paths = request.json.get("pdf_files", [])
        output_file = "/tmp/merged_output.pdf"

        if not pdf_paths:
            print("❌ エラー: PDFファイルが指定されていません")
            return jsonify({"error": "PDFファイルが指定されていません"}), 400

        print(f"📑 {len(pdf_paths)} 個のPDFをマージ中...")

        merger = PdfMerger()
        for pdf in pdf_paths:
            try:
                merger.append(pdf)
            except Exception as e:
                print(f"❌ PDFマージ失敗: {pdf} ({str(e)})")
                return jsonify({"error": f"PDFマージ失敗: {pdf}"}), 400

        merger.write(output_file)
        merger.close()

        elapsed_time = time.time() - start_time
        print(f"✅ PDFマージ完了！処理時間: {elapsed_time:.2f} 秒")

        return jsonify({"message": "✅ PDFマージ完了", "output_file": output_file, "time_taken": elapsed_time})

    except Exception as e:
        error_message = traceback.format_exc()
        print(f"❌ サーバー内部エラー:\n{error_message}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
