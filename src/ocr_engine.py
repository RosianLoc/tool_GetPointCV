import os
import re
import logging
from paddleocr import PaddleOCR

logging.getLogger("ppocr").setLevel(logging.WARNING)

ocr_model = PaddleOCR(lang='en')  # Đổi sang 'en' để nhận diện ký tự Latin/kỹ thuật chính xác hơn

# Ngưỡng confidence tối thiểu - hạ xuống để không bỏ sót text địa chỉ/skill
MIN_CONFIDENCE = 0.4

def extract_text_from_images(image_paths):
    extracted_data = {}

    for img_path in image_paths:
        if not os.path.exists(img_path):
            continue

        label = os.path.splitext(os.path.basename(img_path))[0]

        try:
            result = ocr_model.predict(img_path)
        except Exception as e:
            print(f"Lỗi khi đọc ảnh {label}: {e}")
            continue

        full_text = []

        if result:
            if hasattr(result, '__iter__') and not isinstance(result, list):
                result = list(result)

            for res in result:
                texts, scores = [], []

                if isinstance(res, dict):
                    texts = res.get('rec_texts', [])
                    scores = res.get('rec_scores', [1.0] * len(texts))
                elif hasattr(res, 'rec_texts'):
                    texts = res.rec_texts
                    scores = getattr(res, 'rec_scores', [1.0] * len(texts))
                elif hasattr(res, '__dict__') and 'rec_texts' in res.__dict__:
                    texts = res.__dict__['rec_texts']
                    scores = res.__dict__.get('rec_scores', [1.0] * len(texts))
                elif hasattr(res, 'res') and hasattr(res.res, 'rec_texts'):
                    texts = res.res.rec_texts
                    scores = getattr(res.res, 'rec_scores', [1.0] * len(texts))

                # Chỉ lấy text có confidence >= MIN_CONFIDENCE
                for text, score in zip(texts, scores):
                    if score >= MIN_CONFIDENCE and text.strip():
                        full_text.append(text.strip())

        extracted_data[label] = " ".join(full_text)

    return extracted_data

if __name__ == "__main__":
    import json
    
    folder_path = r"D:\Project\DetectCVLasted\data\cropped_images\2d187349-IT_56"
    
    if os.path.exists(folder_path):
        test_image_paths = [
            os.path.join(folder_path, f) 
            for f in os.listdir(folder_path) 
            if f.endswith('.jpg')
        ]
        
        print(f"Đang chạy OCR để đọc chữ cho {len(test_image_paths)} ảnh...\n")
        cv_raw_text = extract_text_from_images(test_image_paths)
        
        print("--- KẾT QUẢ TRÍCH XUẤT RAW KEY-VALUE ---")
        print(json.dumps(cv_raw_text, ensure_ascii=False, indent=4))
    else:
        print(f"Không tìm thấy thư mục: {folder_path}")