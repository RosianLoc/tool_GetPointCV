import os
import json
import time

# Import các module từ thư mục src
from src.detector import get_cv_boxes
from src.cropper import crop_and_save_regions
from src.ocr_engine import extract_text_from_images
from src.text_processor import clean_cv_data
from src.matcher import calculate_cv_score

def process_cv_pipeline(cv_image_path, jd_criteria):
    """
    Chạy toàn bộ quy trình: YOLO -> Cắt ảnh -> OCR -> Làm sạch -> Chấm điểm
    """
    print(f"\n{'='*50}")
    print(f"BẮT ĐẦU XỬ LÝ CV: {os.path.basename(cv_image_path)}")
    print(f"{'='*50}")
    
    start_time = time.time()

    # Bước 1: YOLO Detect
    print("1. Đang dùng YOLO trích xuất các vùng dữ liệu...")
    cv_regions = get_cv_boxes(cv_image_path)
    if not cv_regions:
        print("-> [LỖI] YOLO không tìm thấy vùng dữ liệu nào.")
        return None

    # Bước 2: Cắt ảnh
    print("2. Đang cắt ảnh theo tọa độ...")
    cropped_image_paths = crop_and_save_regions(cv_image_path, cv_regions)

    # Bước 3: Đọc chữ bằng OCR
    print("3. Đang chạy PaddleOCR để đọc chữ...")
    raw_ocr_data = extract_text_from_images(cropped_image_paths)

    # Bước 4: Làm sạch và chuẩn hóa dữ liệu
    print("4. Đang làm sạch dữ liệu bằng Regex...")
    cleaned_cv_data = clean_cv_data(raw_ocr_data)

    # Bước 5: Matching và chấm điểm
    print("5. Đang đối chiếu với JD và chấm điểm...")
    final_score = calculate_cv_score(cleaned_cv_data, jd_criteria)
    
    end_time = time.time()
    
    # --- IN BÁO CÁO TỔNG KẾT ---
    print(f"\n{'*'*50}")
    print("BÁO CÁO ĐÁNH GIÁ ỨNG VIÊN")
    print(f"{'*'*50}")
    print(json.dumps(cleaned_cv_data, ensure_ascii=False, indent=4))
    print(f"\n[ĐIỂM SỐ]: {final_score['total']}/100")
    print(f"[CHI TIẾT]: Position: {final_score['position']} | Level: {final_score['level']} | Address: {final_score['address']} | GPA: {final_score['gpa']} | Skill: {final_score['skill']}")
    
    if final_score['total'] >= 70:
        print("=> [KẾT LUẬN]: ĐẠT YÊU CẦU, CHUYỂN QUA PHỎNG VẤN!")
    else:
        print("=> [KẾT LUẬN]: HỒ SƠ LOẠI.")
        
    print(f"\nThời gian xử lý: {round(end_time - start_time, 2)} giây")
    print(f"{'='*50}\n")
    
    return final_score

if __name__ == "__main__":
    # --- CẤU HÌNH ĐẦU VÀO ---
    test_image = r"D:\Project\DetectCVLasted\data\raw_cvs\2d187349-IT_56.png"
    
    jd_requirements = {
        "position": "Frontend",
        "level": "Junior",
        "address": "chí minh",
        "gpa": 4.0,
        "skills": ["python", "c++", "react"]
    }
    
    # Chạy hệ thống
    process_cv_pipeline(test_image, jd_requirements)