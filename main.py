import os
import json
import time
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

# Import các module từ thư mục src của bạn
from src.detector import get_cv_boxes
from src.cropper import crop_and_save_regions
from src.ocr_engine import extract_text_from_images
from src.text_processor import clean_cv_data
from src.matcher import calculate_cv_score

# Khởi tạo App FastAPI
app = FastAPI()

def process_cv_pipeline(cv_image_path, jd_criteria_dict):
    """
    Chạy TOÀN BỘ quy trình: YOLO -> Cắt ảnh -> OCR -> Làm sạch -> CHẤM ĐIỂM
    """
    # Bước 1 & 2: Nhận diện và Cắt ảnh
    cv_regions = get_cv_boxes(cv_image_path)
    if not cv_regions:
        return None

    cropped_image_paths = crop_and_save_regions(cv_image_path, cv_regions)
    
    # Bước 3 & 4: Đọc chữ và Làm sạch
    raw_ocr_data = extract_text_from_images(cropped_image_paths)
    cleaned_cv_data = clean_cv_data(raw_ocr_data)
    
    # Bước 5: CHẤM ĐIỂM BẰNG THUẬT TOÁN CỦA PYTHON
    # Dùng fuzzy matching, NLP hoặc logic riêng của bạn ở đây để chấm điểm chính xác nhất
    final_score = calculate_cv_score(cleaned_cv_data, jd_criteria_dict)
    
    # Trả về cả dữ liệu thô và kết quả chấm điểm
    return {
        "extracted_data": cleaned_cv_data,
        "score_details": final_score
    }

# ==========================================
# MỞ API CHO NESTJS GỌI VÀO
# ==========================================
@app.post("/api/extract-cv")
async def extract_cv_api(
    file: UploadFile = File(...), 
    jd_criteria: str = Form(...) # Hứng chuỗi JSON chứa tiêu chí JD từ NestJS
):
    start_time = time.time()
    
    # 1. Lưu file NestJS gửi sang thành file tạm trên ổ cứng Python
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 2. Giải mã chuỗi JSON tiêu chí thành Dictionary của Python
        jd_dict = json.loads(jd_criteria)

        # 3. Chạy Bếp Trưởng (Pipeline AI + Chấm điểm)
        result = process_cv_pipeline(temp_file_path, jd_dict)
        
        if not result:
            raise HTTPException(status_code=400, detail="Không tìm thấy vùng dữ liệu CV")
            
        end_time = time.time()
        print(f"Bóc tách & chấm điểm xong CV {file.filename} trong {round(end_time - start_time, 2)}s")

        # 4. Trả cục JSON về cho NestJS
        # Lưu ý: Cấu trúc này khớp với lúc NestJS gọi sang lấy data
        return JSONResponse(content={
            "success": True,
            "message": "AI trích xuất và chấm điểm thành công",
            "data": result["extracted_data"],               # Dữ liệu chữ để React hiện Form
            "score": result["score_details"]["total"],      # Tổng điểm để NestJS rẽ nhánh (Pass/Fail)
            "score_details": result["score_details"]        # (Tùy chọn) Trả về chi tiết từng phần điểm
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc() # In lỗi ra terminal Python để dễ debug
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 5. Dọn dẹp rác: Xóa file tạm sau khi làm xong
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Chạy server nếu gõ lệnh python main.py
if __name__ == "__main__":
    import uvicorn
    # Mở port 8000 lắng nghe NestJS
    uvicorn.run(app, host="0.0.0.0", port=8000)