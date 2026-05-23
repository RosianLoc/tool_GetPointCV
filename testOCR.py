import os
import re
import json
import logging
import unicodedata
from paddleocr import PaddleOCR

# ================= CẤU HÌNH & TỪ ĐIỂN =================
CROP_DIR = r"data\cropped_images"
MIN_CONFIDENCE = 0.4

# Tắt log rác của PaddleOCR
logging.getLogger("ppocr").setLevel(logging.WARNING)

from src.ocr_engine import extract_text_from_images
from src.text_processor import clean_cv_data

if __name__ == "__main__":
    print("🚀 Đang khởi tạo PaddleOCR (Ngôn ngữ: vi)...")
    ocr_model = PaddleOCR(lang='vi')

    # Lấy danh sách các thư mục con trong cropped_images (mỗi thư mục là 1 CV)
    cv_folders = [f for f in os.listdir(CROP_DIR) if os.path.isdir(os.path.join(CROP_DIR, f))]
    print(f"\n📦 Tìm thấy {len(cv_folders)} CV đã được cắt. Bắt đầu đọc chữ...\n")

    for cv_name in cv_folders:
        folder_path = os.path.join(CROP_DIR, cv_name)
        img_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.png')]
        
        print("="*60)
        print(f"📄 CV ĐANG XỬ LÝ: {cv_name}")
        
        # 1. OCR bóc tách (RAW)
        raw_text_data = extract_text_from_images(img_paths)
        
        # 2. Xử lý dọn dẹp nhãn và sửa lỗi chính tả (CLEAN)
        cleaned_text_data = clean_cv_data(raw_text_data)

        print("\n--- 🔴 DỮ LIỆU THÔ TỪ OCR (RAW) ---")
        print(json.dumps(raw_text_data, ensure_ascii=False, indent=4))
        
        print("\n--- 🟢 DỮ LIỆU ĐÃ LỌC & SỬA LỖI (CLEANED) ---")
        print(json.dumps(cleaned_text_data, ensure_ascii=False, indent=4))
        print("="*60 + "\n")