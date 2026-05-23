import os
import json
import time
import shutil
import asyncio
import fitz  # pymupdf
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

# Import các module từ thư mục src của bạn
from src.detector import get_cv_boxes
from src.cropper import crop_and_save_regions
from src.ocr_engine import extract_text_from_images
from src.text_processor import clean_cv_data
from src.matcher import calculate_cv_score
from src.pdf_extractor import extract_cv_from_pdf


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
        # DPI 300 để ảnh render ra có kích thước gần với ảnh screenshot (training data)
        dpi = 300
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)  # alpha=False -> RGB thuần, không có kênh trong suốt
        out_path = file_path + '_page0.png'
        pix.save(out_path)
        doc.close()
        
        print(f"📄 [PDF->IMG] Đã convert PDF sang ảnh: {pix.width}x{pix.height}px @ {dpi} DPI")
        return out_path

    raise HTTPException(
        status_code=400,
        detail=f"Định dạng file '{ext}' không được hỗ trợ. Vui lòng upload PDF, PNG, JPG."
    )

# Khởi tạo App FastAPI
app = FastAPI()

async def check_nestjs_connection(host="127.0.0.1", port=5000, retries=5, delay=2):
    print(f"\n📡 [NETWORK] Đang kiểm tra kết nối thực tế tới NestJS ({host}:{port})...")
    for attempt in range(1, retries + 1):
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            print("🤝 [SUCCESS] ĐÃ KẾT NỐI TỚI NESTJS SERVER THÀNH CÔNG!")
            return True
        except (ConnectionRefusedError, OSError):
            print(f"⚠️ [CẢNH BÁO] Chưa kết nối được NestJS (Lần {attempt}/{retries}). Đang chờ NestJS bật lên...")
            await asyncio.sleep(delay)
            
    print("❌ [LỖI] KHÔNG THỂ KẾT NỐI TỚI NESTJS SERVER SAU NHIỀU LẦN THỬ!")
    print("👉 Hãy chắc chắn bạn đã bật server NestJS (ví dụ: npm run start:dev)")
    return False

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*70)
    print("🚀 [SYSTEM] ĐANG KHỞI ĐỘNG PYTHON AI SERVER...")
    print("✅ [CHECK] Đã tải module YOLO (Nhận diện bố cục CV) - OK")
    print("✅ [CHECK] Đã tải OCR Engine (Trích xuất văn bản) - OK")
    print("✅ [CHECK] Đã khởi tạo Text Processor & Matcher - OK")
    print("🌟 [SUCCESS] PYTHON SERVER ĐÃ BẬT XONG VÀ ĐANG CHẠY Ở PORT 8000!")
    
    # Kiểm tra kết nối thật
    is_connected = await check_nestjs_connection()
    if is_connected:
        print("✅ Hệ thống AI đã sẵn sàng nhận CV và JD từ NestJS!")
    else:
        print("⚠️ Hệ thống AI đang chạy tĩnh, chưa thể giao tiếp với NestJS lúc này.")
    print("="*70 + "\n")

def _fallback_find_gpa_from_image(image_path):
    """
    Fallback: Khi YOLO không detect được box GPA,
    OCR toàn bộ ảnh rồi tìm GPA bằng regex.
    Hỗ trợ cả format tiếng Việt và tiếng Anh.
    """
    import re
    try:
        from src.ocr_engine import ocr_model
        result = ocr_model.predict(image_path)
        
        full_text = []
        if result:
            for res in (list(result) if not isinstance(result, list) else result):
                texts = []
                if isinstance(res, dict):
                    texts = res.get('rec_texts', [])
                elif hasattr(res, 'rec_texts'):
                    texts = res.rec_texts
                elif hasattr(res, '__dict__') and 'rec_texts' in res.__dict__:
                    texts = res.__dict__['rec_texts']
                elif hasattr(res, 'res') and hasattr(res.res, 'rec_texts'):
                    texts = res.res.rec_texts
                full_text.extend([t.strip() for t in texts if t.strip()])
        
        all_text = ' '.join(full_text)
        print(f"🔍 [FALLBACK GPA] OCR toàn ảnh: {len(all_text)} ký tự")
        
        # Tìm GPA bằng nhiều pattern (hỗ trợ cả EN và VN)
        gpa_patterns = [
            r'GPA\s*[:\-]?\s*(\d+[.,]\d+)\s*/\s*(?:4\.0|10)',
            r'GPA\s*[:\-]?\s*(\d+[.,]\d+)',
            r'CGPA\s*[:\-]?\s*(\d+[.,]\d+)',
            r'(\d+[.,]\d+)\s*/\s*4\.0',
            r'Grade\s*[:\-]?\s*(\d+[.,]\d+)',
        ]
        
        for pattern in gpa_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                gpa_val = match.group(1).replace(',', '.')
                print(f"✅ [FALLBACK GPA] Tìm thấy GPA = {gpa_val}")
                return gpa_val
        
        print("❌ [FALLBACK GPA] Không tìm thấy GPA trong toàn bộ ảnh")
        return '0'
        
    except Exception as e:
        print(f"❌ [FALLBACK GPA] Lỗi khi OCR toàn ảnh: {e}")
        return '0'


def process_cv_pipeline(cv_image_path, jd_criteria_dict):
    """
    Chạy TOÀN BỘ quy trình: YOLO -> Cắt ảnh -> OCR -> Làm sạch -> CHẤM ĐIỂM
    """
    # Bước 1 & 2: Nhận diện và Cắt ảnh
    cv_regions = get_cv_boxes(cv_image_path)
    if not cv_regions:
        return None

    # Kiểm tra xem YOLO có detect được GPA không
    detected_labels = [r['label'] for r in cv_regions]
    has_gpa_box = 'gpa' in detected_labels

    cropped_image_paths = crop_and_save_regions(cv_image_path, cv_regions)
    
    # Bước 3 & 4: Đọc chữ và Làm sạch
    raw_ocr_data = extract_text_from_images(cropped_image_paths)

    # FALLBACK: Nếu YOLO không detect được GPA → OCR toàn ảnh để tìm
    if not has_gpa_box:
        print("🔄 [FALLBACK] YOLO không detect GPA, đang OCR toàn ảnh tìm GPA...")
        fallback_gpa = _fallback_find_gpa_from_image(cv_image_path)
        if fallback_gpa != '0':
            raw_ocr_data['gpa'] = fallback_gpa

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

def process_pdf_pipeline(pdf_path, jd_criteria_dict):
    """
    Pipeline dành riêng cho PDF: Đọc text trực tiếp từ PDF (không cần YOLO).
    Text trong PDF là kỹ thuật số nên không bị lỗi OCR.
    """
    # Bước 1: Trích xuất text trực tiếp từ PDF
    raw_pdf_data = extract_cv_from_pdf(pdf_path)
    
    if not raw_pdf_data:
        print("⚠️ [PDF] Không trích xuất được text từ PDF, thử fallback sang YOLO...")
        return None
    
    print("\n--- [PDF RAW] DỮ LIỆU TRƯỚC KHI CLEAN ---")
    for k, v in raw_pdf_data.items():
        print(f"  [{k}] -> '{v[:80]}...'" if len(str(v)) > 80 else f"  [{k}] -> '{v}'")
    print("--------------------------------------\n")
    
    # Bước 2: Làm sạch (dùng chung clean_cv_data)
    cleaned_cv = clean_cv_data(raw_pdf_data)
    
    print("--- [PDF CLEANED] DỮ LIỆU SAU KHI CLEAN ---")
    for k, v in cleaned_cv.items():
        print(f"  [{k}] -> '{v}'")
    print("---------------------------------------\n")
    
    # Bước 3: Chấm điểm
    final_score = calculate_cv_score(cleaned_cv, jd_criteria_dict)
    
    return {
        "extracted_data": cleaned_cv,
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

        # 2b. Chọn pipeline phù hợp theo loại file
        file_ext = os.path.splitext(temp_file_path)[1].lower()
        
        if file_ext == '.pdf':
            # PDF → Đọc text trực tiếp (bypass YOLO hoàn toàn)
            print("📄 [PIPELINE] Sử dụng PDF Text Extractor (Bypass YOLO)")
            result = process_pdf_pipeline(temp_file_path, jd_dict)
            
            # Fallback: Nếu PDF không có text (PDF scan/ảnh) → convert sang ảnh rồi dùng YOLO
            if not result:
                print("🔄 [FALLBACK] PDF không có text, chuyển sang YOLO pipeline...")
                converted_image_path = convert_to_image(temp_file_path)
                result = process_cv_pipeline(converted_image_path, jd_dict)
        else:
            # Ảnh → YOLO pipeline (như cũ)
            print("🖼️ [PIPELINE] Sử dụng YOLO + OCR pipeline")
            converted_image_path = convert_to_image(temp_file_path)
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