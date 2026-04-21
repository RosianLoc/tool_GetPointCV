import os
import logging
from paddleocr import PaddleOCR

# Tắt log rác
logging.getLogger("ppocr").setLevel(logging.WARNING)

# Khởi tạo model
ocr_model = PaddleOCR(lang='vi')

def extract_text_from_images(image_paths):
    extracted_data = {}
    
    for img_path in image_paths:
        if not os.path.exists(img_path):
            continue
            
        filename = os.path.basename(img_path)
        label = os.path.splitext(filename)[0]
        
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
                # KIỂM TRA ĐÚNG CẤU TRÚC PADDLEX (CÓ CHỮ 'S')
                if isinstance(res, dict):
                    if 'rec_texts' in res:
                        full_text.extend(res['rec_texts'])
                elif hasattr(res, 'rec_texts'):
                    full_text.extend(res.rec_texts)
                elif hasattr(res, '__dict__') and 'rec_texts' in res.__dict__:
                    full_text.extend(res.__dict__['rec_texts'])
                # Cấu trúc fallback phòng hờ
                elif hasattr(res, 'res') and hasattr(res.res, 'rec_texts'):
                    full_text.extend(res.res.rec_texts)

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