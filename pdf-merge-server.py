import requests
import time
import traceback
import os
import re
from flask import Flask, request, jsonify
from PyPDF2 import PdfMerger

app = Flask(__name__)

# 🚀 ファイル名をサニタイズする関数
def sanitize_filename(filename):
    return re.sub(r'[\\/:*?"<>|]', '_', filename)

@app.route("/", methods=["GET"])
def home():
    return "✅ PDF Merge API が実行されています!"

@app.route("/merge_pdfs", methods=["POST"])
def merge_pdfs():
    start_time = time.time()
    try:
        pdf_urls = request.json.get("pdf_files", [])
        output_file = "/tmp/merged_output.pdf"

        if not pdf_urls:
            print("❌ エラー: PDFファイルのURLが指定されていません")
            return jsonify({"error": "PDFファイルのURLが指定されていません"}), 400

        print(f"📥 {len(pdf_urls)}個のPDFをダウンロード開始...")

        temp_pdf_files = []
        for i, pdf_url in enumerate(pdf_urls):
            print(f"🚀 ダウンロード開始: {pdf_url}")

            try:
                response = requests.get(pdf_url, stream=True)
            except Exception as e:
                print(f"❌ リクエストエラー: {pdf_url} ({str(e)})")
                return jsonify({"error": f"リクエストエラー: {pdf_url}"}), 400

            print(f"🔍 ステータスコード: {response.status_code}")
            print(f"🔍 Content-Type: {response.headers.get('Content-Type')}")

            if response.status_code != 200:
                print(f"❌ ダウンロード失敗: {pdf_url} (ステータスコード: {response.status_code})")
                return jsonify({"error": f"ダウンロード失敗: {pdf_url}"}), 400

            # 🚀 ファイル名をサニタイズ
            pdf_name = f"temp_pdf_{i}.pdf"  # 仮の名前（本来はURLから名前を取得）
            sanitized_name = sanitize_filename(pdf_name)
            temp_path = f"/tmp/{sanitized_name}"

            with open(temp_path, "wb") as f:
                f.write(response.content)

            temp_pdf_files.append(temp_path)
            print(f"✅ {pdf_url} → {temp_path} 保存完了")

        print(f"📑 PDFをマージ中...")

        merger = PdfMerger()
        for pdf in temp_pdf_files:
            try:
                merger.append(pdf)
            except Exception as e:
                print(f"❌ PDFマージ失敗: {pdf} ({str(e)})")
                return jsonify({"error": f"PDFマージ失敗: {pdf}"}), 400

        merger.write(output_file)
        merger.close()

        for pdf in temp_pdf_files:
            os.remove(pdf)

        elapsed_time = time.time() - start_time
        print(f"✅ PDFマージ完了！処理時間: {elapsed_time:.2f} 秒")

        return jsonify({"message": "✅ PDFマージ完了", "output_file": output_file, "time_taken": elapsed_time})

    except Exception as e:
        error_message = traceback.format_exc()
        print(f"❌ サーバー内部エラー:\n{error_message}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
