import os
import logging
from paddleocr import PaddleOCR

# Tắt bớt log rác
logging.getLogger("ppocr").setLevel(logging.WARNING)

print("Đang load model...")
ocr_model = PaddleOCR(lang='vi')

# Lấy 1 ảnh bất kỳ (ví dụ ảnh gpa) để soi dữ liệu
img_path = r"D:\Project\DetectCVLasted\data\cropped_images\2d187349-IT_56\gpa.jpg"

if os.path.exists(img_path):
    print(f"\nĐang đọc ảnh: {img_path}")
    result = ocr_model.predict(img_path)
    
    print("\n" + "="*40)
    print(" CẤU TRÚC DỮ LIỆU GỐC (RAW DATA)")
    print("="*40)
    
    # Ép sang list và in ra mọi thứ nó có
    result_list = list(result)
    for i, item in enumerate(result_list):
        print(f"\n--- Phần tử thứ {i} ---")
        print(f"Kiểu dữ liệu (Type): {type(item)}")
        print(f"Giá trị (Value): {item}")
        
        # Nếu nó là một Object (kiểu mới của PaddleX), in luôn các thuộc tính ẩn
        if hasattr(item, '__dict__'):
            print(f"Thuộc tính ẩn (Attributes): {item.__dict__}")
else:
    print(f"Không tìm thấy ảnh tại: {img_path}. Bạn kiểm tra lại đường dẫn nhé!")