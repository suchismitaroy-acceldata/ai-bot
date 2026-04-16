import os
import zipfile
import requests
from extractor import extract_text

documents = []
MAX_DOCS = 50  # safe limit

# 🔥 PASTE YOUR GOOGLE DRIVE LINK HERE
ZIP_URL = "https://drive.google.com/uc?export=download&id=11Y4bygYs7XKfJ9HYP92aCbnBbTMQGEkn"


def download_zip(zip_path):
    if os.path.exists(zip_path):
        print("✅ ZIP already exists")
        return

    print("⬇️ Downloading ZIP...")

    response = requests.get(ZIP_URL, stream=True)

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print("✅ Download complete")


def build_index():
    global documents

    BASE_PATH = os.getcwd()
    zip_path = os.path.join(BASE_PATH, "sales_docs.zip")
    data_path = os.path.join(BASE_PATH, "data")

    print("📁 Working dir:", BASE_PATH)

    # 🔥 DOWNLOAD ZIP
    download_zip(zip_path)

    # 🔥 EXTRACT ZIP
    if not os.path.exists(data_path):
        print("📦 Extracting ZIP...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_path)

    print("📁 Data contents:", os.listdir(data_path))

    documents = []
    count = 0

    for root, dirs, files in os.walk(data_path):
        print("📂 Folder:", root)

        for file in files:

            if count >= MAX_DOCS:
                break

            if file.lower().endswith((".pdf", ".docx", ".pptx", ".txt")):

                full_path = os.path.join(root, file)
                print("📄 Processing:", file)

                try:
                    text = extract_text(full_path)

                    if text.strip():
                        documents.append({
                            "name": file,
                            "content": text.lower()
                        })
                        count += 1

                except Exception as e:
                    print("❌ Skipped:", file, e)

    print("✅ Total documents loaded:", count)


def search(query, top_k=5):
    query = query.lower()
    results = []

    for doc in documents:
        score = 0

        if query in doc["name"]:
            score += 5

        if query in doc["content"]:
            score += 3

        for word in query.split():
            if word in doc["content"]:
                score += 1

        if score > 0:
            results.append((score, doc))

    results.sort(key=lambda x: x[0], reverse=True)

    return [r[1] for r in results[:top_k]]