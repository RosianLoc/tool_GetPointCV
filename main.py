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

def process_cv_pipeline(cv_image_path):
    """
    Pipeline bây giờ chỉ cần làm đến đoạn Clean Data (Bước 4)
    Vì việc tính điểm (Bước 5) mình đã dời sang NestJS để chống gian lận Form
    """
    cv_regions = get_cv_boxes(cv_image_path)
    if not cv_regions:
        return None

    cropped_image_paths = crop_and_save_regions(cv_image_path, cv_regions)
    raw_ocr_data = extract_text_from_images(cropped_image_paths)
    cleaned_cv_data = clean_cv_data(raw_ocr_data)
    
    return cleaned_cv_data

# ==========================================
# MỞ API CHO NESTJS GỌI VÀO
# ==========================================
@app.post("/api/extract-cv")
async def extract_cv_api(
    file: UploadFile = File(...), 
    jd_criteria: str = Form(...) # Nhận tiêu chí JD từ NestJS gửi sang (dù không dùng tính điểm nhưng cứ hứng để đó)
):
    start_time = time.time()
    
    # 1. Lưu file NestJS gửi sang thành file tạm trên ổ cứng Python
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 2. Chạy Bếp Trưởng (Pipeline AI)
        cleaned_data = process_cv_pipeline(temp_file_path)
        
        if not cleaned_data:
            raise HTTPException(status_code=400, detail="Không tìm thấy vùng dữ liệu CV")
            
        end_time = time.time()
        print(f"Bóc tách xong CV {file.filename} trong {round(end_time - start_time, 2)}s")

        # 3. Trả cục JSON nháp về cho NestJS
        return JSONResponse(content={
            "success": True,
            "data": cleaned_data,
            "message": "Trích xuất AI thành công"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # 4. Dọn dẹp rác: Xóa file tạm sau khi làm xong
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Chạy server nếu gõ lệnh python main.py
if __name__ == "__main__":
    import uvicorn
    # Mở port 8000 lắng nghe NestJS
    uvicorn.run(app, host="0.0.0.0", port=8000)