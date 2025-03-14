import requests
import time
import traceback
from flask import Flask, request, jsonify
from PyPDF2 import PdfMerger, PdfReader
import os

app = Flask(__name__)

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
            print(f"🔍 最初の100バイト: {response.content[:100]}")  # HTMLの可能性をチェック

            if response.status_code != 200:
                print(f"❌ ダウンロード失敗: {pdf_url} (ステータスコード: {response.status_code})")
                return jsonify({"error": f"ダウンロード失敗: {pdf_url}"}), 400

            temp_path = f"/tmp/temp_pdf_{i}.pdf"
            with open(temp_path, "wb") as f:
                f.write(response.content)

            # ✅ PDFとして開けるかチェック
            try:
                with open(temp_path, "rb") as f:
                    PdfReader(f)
            except Exception as e:
                print(f"❌ 無効なPDF: {pdf_url} ({str(e)})")
                os.remove(temp_path)  # 破損ファイルは削除
                return jsonify({"error": f"無効なPDF: {pdf_url}"}), 400

            temp_pdf_files.append(temp_path)
            print(f"✅ {pdf_url} ダウンロード完了")

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
