import requests
import time  # 🕒 時間計測用
import traceback  # ❌ エラー詳細を取得
from flask import Flask, request, jsonify
from PyPDF2 import PdfMerger
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ PDF Merge API が実行されています!"

@app.route("/merge_pdfs", methods=["POST"])
def merge_pdfs():
    start_time = time.time()  # 🕒 開始時間記録
    try:
        pdf_urls = request.json.get("pdf_files", [])  # JSONデータを取得
        output_file = "/tmp/merged_output.pdf"

        if not pdf_urls:
            return jsonify({"error": "PDFファイルのURLが指定されていません"}), 400

        print(f"📥 {len(pdf_urls)}個のPDFをダウンロード開始...")

        temp_pdf_files = []
        for i, pdf_url in enumerate(pdf_urls):
            response = requests.get(pdf_url, stream=True)  # 🕒 ストリーミングダウンロード
            if response.status_code != 200:
                print(f"❌ ダウンロード失敗: {pdf_url} (ステータスコード: {response.status_code})")
                return jsonify({"error": f"ダウンロード失敗: {pdf_url}"}), 400

            temp_path = f"/tmp/temp_pdf_{i}.pdf"
            with open(temp_path, "wb") as f:
                f.write(response.content)

            temp_pdf_files.append(temp_path)
            print(f"✅ {pdf_url} ダウンロード完了")

        print(f"📑 PDFをマージ中...")

        merger = PdfMerger()
        for pdf in temp_pdf_files:
            merger.append(pdf)
        merger.write(output_file)
        merger.close()

        for pdf in temp_pdf_files:
            os.remove(pdf)

        elapsed_time = time.time() - start_time  # 🕒 経過時間計算
        print(f"✅ PDFマージ完了！処理時間: {elapsed_time:.2f} 秒")

        return jsonify({"message": "✅ PDFマージ完了", "output_file": output_file, "time_taken": elapsed_time})

    except Exception as e:
        error_message = traceback.format_exc()  # ❌ エラー詳細を取得
        print(f"❌ サーバー内部エラー:\n{error_message}")  # Renderのログに出力
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
