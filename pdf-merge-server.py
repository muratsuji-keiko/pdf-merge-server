import base64
import time
import traceback
from flask import Flask, request, jsonify
from PyPDF2 import PdfMerger
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ PDF Merge API が実行されています!"

@app.route("/merge_pdfs", methods=["POST"])
def merge_pdfs():
    start_time = time.time()
    try:
        pdf_files = request.json.get("pdf_files", [])
        output_file = "/tmp/merged_output.pdf"

        if not pdf_files:
            print("❌ エラー: PDFデータが指定されていません")
            return jsonify({"error": "PDFデータが指定されていません"}), 400

        print(f"📥 {len(pdf_files)}個のPDFを受信...")

        temp_pdf_files = []
        for i, pdf in enumerate(pdf_files):
            filename = pdf["filename"]
            pdf_data = base64.b64decode(pdf["data"])

            temp_path = f"/tmp/{filename}"
            with open(temp_path, "wb") as f:
                f.write(pdf_data)

            temp_pdf_files.append(temp_path)
            print(f"✅ {filename} 保存完了")

        print(f"📑 PDFをマージ中...")

        merger = PdfMerger()
        for pdf in temp_pdf_files:
            merger.append(pdf)

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
