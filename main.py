import os
import json
import time
import shutil
import fitz  # pymupdf
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

# Import các module từ thư mục src của bạn
from src.detector import get_cv_boxes
from src.cropper import crop_and_save_regions
from src.ocr_engine import extract_text_from_images
from src.text_processor import clean_cv_data
from src.matcher import calculate_cv_score


def convert_to_image(file_path: str) -> str:
    """
    Nếu file là PDF/DOC/DOCX thì convert trang đầu tiên sang PNG.
    Nếu đã là ảnh thì trả về nguyên đường dẫn.
    Trả về đường dẫn file ảnh để YOLO xử lý.
    """
    ext = os.path.splitext(file_path)[1].lower()
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp'}

    if ext in image_extensions:
        return file_path

    if ext == '.pdf':
        doc = fitz.open(file_path)
        page = doc[0]  # Lấy trang đầu tiên
        # DPI 200 đủ để YOLO detect tốt, không quá nặng
        mat = fitz.Matrix(200 / 72, 200 / 72)
        pix = page.get_pixmap(matrix=mat)
        out_path = file_path + '_page0.png'
        pix.save(out_path)
        doc.close()
        return out_path

    raise HTTPException(
        status_code=400,
        detail=f"Định dạng file '{ext}' không được hỗ trợ. Vui lòng upload PDF, PNG, JPG."
    )

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

    print("\n--- [RAW OCR] DỮ LIỆU TRƯỚC KHI CLEAN ---")
    for k, v in raw_ocr_data.items():
        print(f"  [{k}] -> '{v}'")
    print("--------------------------------------\n")

    cleaned_cv_data = clean_cv_data(raw_ocr_data)

    print("--- [CLEANED] DỮ LIỆU SAU KHI CLEAN ---")
    for k, v in cleaned_cv_data.items():
        print(f"  [{k}] -> '{v}'")
    print("---------------------------------------\n")
    
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
    converted_image_path = None
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # 2. Giải mã chuỗi JSON tiêu chí thành Dictionary của Python
        jd_dict = json.loads(jd_criteria)

        print("\n========== [NESTJS -> PYTHON] JD NHAN DUOC ==========")
        print(f"File CV: {file.filename} | Content-Type: {file.content_type}")
        print(f"JD Criteria ({len(jd_dict)} truong):")
        for k, v in jd_dict.items():
            print(f"  [{k}] -> {v}")
        print("=====================================================\n")

        # 2b. Convert PDF/DOC sang ảnh nếu cần
        converted_image_path = convert_to_image(temp_file_path)

        # 3. Chạy Bếp Trưởng (Pipeline AI + Chấm điểm)
        result = process_cv_pipeline(converted_image_path, jd_dict)
        
        if not result:
            raise HTTPException(status_code=400, detail="Không tìm thấy vùng dữ liệu CV")

        print("\n========== [PYTHON DETECT] DU LIEU TRICH XUAT TU CV ==========")
        for section, content in result["extracted_data"].items():
            print(f"  [{section}] -> {content}")
        print("==============================================================\n")

        print("\n========== [MATCHING] SO KHOP JD vs CV ==========")
        for field, detail in result["score_details"].items():
            if field == "total":
                continue
            jd_val = jd_dict.get(field, "(khong co trong JD)")
            cv_val = detail.get("cv_value", "(khong detect duoc)") if isinstance(detail, dict) else "N/A"
            score  = detail.get("score", detail) if isinstance(detail, dict) else detail
            print(f"  [{field}]")
            print(f"    JD yeu cau : {jd_val}")
            print(f"    CV co      : {cv_val}")
            print(f"    Diem       : {score}")
        print(f"  -> TONG DIEM: {result['score_details'].get('total', 'N/A')}")
        print("=================================================\n")

        end_time = time.time()
        print(f"Hoan tat CV '{file.filename}' trong {round(end_time - start_time, 2)}s")

        print("\n--- CHI TIET DIEM PYTHON CHAM ---")
        print(json.dumps(result["score_details"], indent=4, ensure_ascii=False))
        print("---------------------------------\n")

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
        # Xóa cả file ảnh đã convert nếu khác file gốc
        if converted_image_path and converted_image_path != temp_file_path and os.path.exists(converted_image_path):
            os.remove(converted_image_path)

# Chạy server nếu gõ lệnh python main.py
if __name__ == "__main__":
    import uvicorn
    # Mở port 8000 lắng nghe NestJS
    uvicorn.run(app, host="0.0.0.0", port=8000)