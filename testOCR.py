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

OCR_CORRECTIONS = {
    # Lỗi vị trí, cấp bậc
    r'\bsyster\b': 'system', r'\bsytem\b': 'system', r'\bsysem\b': 'system',
    r'\badministrato\b': 'administrator', r'\badministrat\b': 'administrator', r'\badministrtor\b': 'administrator',
    r'\benginer\b': 'engineer', r'\bengineer\b': 'engineer', r'\bsEngineer\b': 'Engineer',
    r'\bdeveloer\b': 'developer', r'\bdevelper\b': 'developer', r'\bUevelope\b': 'Developer', r'\bDevelope\b': 'Developer',
    r'\bdesigher\b': 'designer', r'\bfronend\b': 'frontend', r'\bfrontnd\b': 'frontend', r'\bbacknd\b': 'backend', r'\bfullstck\b': 'fullstack',
    r'\bsenoir\b': 'senior', r'\bjunoir\b': 'junior', r'\bSunior\b': 'Junior',
    r'\bfreshr\b': 'fresher', r'\bintrn\b': 'intern', r'\bIntem\b': 'Intern', r'\bInter\b': 'Intern', r'\bnter\b': 'Intern', r'\bmidl\b': 'middle',
    r'\bAl Engineer\b': 'AI Engineer',
    
    # Lỗi ngôn ngữ / công nghệ
    r'\blava\b': 'java', r'\bjave\b': 'java',
    r'\bjavascrint\b': 'javascript', r'\bjavascrit\b': 'javascript', r'\bjavascritp\b': 'javascript',
    r'\btypescrit\b': 'typescript', r'\bpythn\b': 'python', 
    r'\breact\.js\b': 'reactjs', r'\breactis\b': 'reactjs', 
    r'\bnode\.js\b': 'nodejs', r'\bnodeis\b': 'nodejs', r'\bvue\.js\b': 'vuejs', r'\bangulr\b': 'angular', r'\bnestis\b': 'nestjs',
    r'\blarave\b': 'laravel', r'\bspringboot\b': 'spring boot', 
    r'\bcl/cd\b': 'ci/cd', r'\bc1/cd\b': 'ci/cd', r'\bcicd\b': 'ci/cd', 
    r'\bdockr\b': 'docker', r'\bkuberntes\b': 'kubernetes', r'\bk8s\b': 'kubernetes', r'\bterrafom\b': 'terraform',
    r'\bmongdb\b': 'mongodb', r'\bpostgres\b': 'postgresql', r'\bmysq\b': 'mysql',
    r'\bgitub\b': 'github', r'\bfigm\b': 'figma', r'\blinx\b': 'linux', r'\bwindws\b': 'windows',
    r'\bsowae\b': 'software', r'\bsoftwar\b': 'software', r'\bsofware\b': 'software',
    r'\bsCSs\b': 'SCSS', r'\bSCSs\b': 'SCSS', r'\bHTMl\b': 'HTML', r'\bHTMl5\b': 'HTML5',
    r'\bVisud Studio\b': 'Visual Studio', r'\bUnredlEngine\b': 'Unreal Engine',
    
    # Lỗi Kỹ năng mềm & Các trường khác
    r'\bKy năng\b': 'Kỹ năng', r'\bK năng\b': 'Kỹ năng', r'\bK näng\b': 'Kỹ năng', r'\bKý näng\b': 'Kỹ năng', r'\bKy näng\b': 'Kỹ năng',
    r'\bKnăng mm\b': 'Kỹ năng mềm', r'\bC8ng cu\b': 'Công cụ', r'\bcơ bàn\b': 'cơ bản',
    r'\bLàm vic nhóm\b': 'Làm việc nhóm', r'\blānh đgo nhóm\b': 'Lãnh đạo nhóm', r'\bqun lý thi gian\b': 'Quản lý thời gian', r'\bquan lý thi gian\b': 'Quản lý thời gian',
    r'\bChuyanngann\b': 'Chuyên ngành', r'\bChuyenngann\b': 'Chuyên ngành', r'\bhuyenngann\b': 'Chuyên ngành',
    r'\bD án tótnahi8r\b': 'Đồ án tốt nghiệp', r'\bDi án tót nabi8\b': 'Đồ án tốt nghiệp',
    
    # Lỗi Địa chỉ, Thành phố, Quốc gia
    r'\bThành ph H ChrMinh\b': 'Thành phố Hồ Chí Minh', r'\bThành ph H Ch Minh\b': 'Thành phố Hồ Chí Minh', r'\bThnh ph H Chl Minh\b': 'Thành phố Hồ Chí Minh',
    r'\bThành phó H ChrMinh\b': 'Thành phố Hồ Chí Minh', r'\bThnh phó H ChrMinh\b': 'Thành phố Hồ Chí Minh', r'\bThành phH Chl Minh\b': 'Thành phố Hồ Chí Minh',
    r'\bThnh ph H Chr Minh\b': 'Thành phố Hồ Chí Minh', r'\bthành ph H Chl Minh\b': 'Thành phố Hồ Chí Minh', r'\bThnh ph H\b': 'Thành phố Hồ', r'\bThành phó H Ch\(Minh\b': 'Thành phố Hồ Chí Minh',
    r'\bH8 Chí Minh\b': 'Hồ Chí Minh', r'\bH ChrMinh\b': 'Hồ Chí Minh', r'\bH Chr Minh\b': 'Hồ Chí Minh', r'\bH Chl Minh\b': 'Hồ Chí Minh',
    r'\bVit Nam\b': 'Việt Nam', r'\bViBt Nam\b': 'Việt Nam', r'\bViBt Nom\b': 'Việt Nam', r'\bViêt Nam\b': 'Việt Nam', r'\bVi8t Nam\b': 'Việt Nam',
    r'\bPhưng\b': 'Phường', r'\bPhưòng\b': 'Phường', r'\bQun\b': 'Quận', r'\bQuġn\b': 'Quận', r'\bquiw Qun\b': 'Quận',
    r'\bTn Phú\b': 'Tân Phú', r'\bTân Ph\b': 'Tân Phú', r'\bTn Phù\b': 'Tân Phú', r'\bTn Binh\b': 'Tân Bình', r'\bPh Nhun\b': 'Phú Nhuận', r'\bPhú Nhun\b': 'Phú Nhuận',
    r'\bPh Thαnh\b': 'Phú Thạnh', r'\bHa Thơnh\b': 'Hòa Thạnh', r'\bHm\b': 'Hẻm',
    r'\bqun\b': 'quan', r'\bquan\b': 'quan', r'\bh chi minh\b': 'ho chi minh', r'\bh\.chi minh\b': 'ho chi minh', r'\bhcm\b': 'ho chi minh', r'\btp\.hcm\b': 'ho chi minh',
    r'\bha noi\b': 'ha noi', r'\bhn\b': 'ha noi', r'\bphuong\b': 'phuong', r'\bduong\b': 'duong',
    r'\bSeniorCybersecurity\b': 'Senior Cybersecurity', r'\bKhu Phó\b': 'Khu Phố', r'\bCách Mang\b': 'Cách Mạng',
    r'\bChl Minh\b': 'Chí Minh', r'\bquiw\b': '', r'\bHin Vương\b': 'Hiền Vương',
    r'\bEUUDDUUBN\b': '',
}

ADDRESS_KEYWORDS = ['quận', 'qun', 'q.', 'phố', 'hồ chí minh', 'ho chi minh', 'h chi minh', 'hà nội', 'ha noi', 'hcm', 'tp.hcm', 'thành phố', 'thanh pho', 'phường', 'phuong', 'đường', 'duong', 'tỉnh', 'district', 'city', 'street', 'quận 1', 'quận 2', 'quận 3', 'quận 4', 'quận 5', 'quận 6', 'quận 7', 'việt nam', 'viet nam', 'vi8t nam', 'thanh phó', 'hó chl minh', 'hó chi minh']
POSITION_KEYWORDS = ['engineer', 'developer', 'designer', 'manager', 'analyst', 'lead', 'architect', 'devops', 'frontend', 'backend', 'fullstack', 'software', 'system', 'data', 'kỹ sư', 'lập trình']
KNOWN_LEVELS = ['intern', 'fresher', 'junior', 'middle', 'mid', 'senior', 'lead', 'manager']
# ======================================================

def extract_text_from_images(image_paths, ocr_model):
    extracted_data = {}
    for img_path in image_paths:
        if not os.path.exists(img_path): continue
        label = os.path.splitext(os.path.basename(img_path))[0]
        
        try:
            result = ocr_model.predict(img_path)
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

                    for text, score in zip(texts, scores):
                        if score >= MIN_CONFIDENCE and text.strip():
                            full_text.append(text.strip())
            extracted_data[label] = " ".join(full_text)
        except Exception as e:
            print(f"❌ Lỗi khi đọc ảnh {label}: {e}")
    return extracted_data

# --- Các hàm dọn dẹp logic (Giữ nguyên của bạn) ---
def _has_address(text): return any(kw in text.lower() for kw in ADDRESS_KEYWORDS)
def _has_position(text): return any(kw in text.lower() for kw in POSITION_KEYWORDS)
def _has_level(text): return any(lvl in text.lower().split() for lvl in KNOWN_LEVELS)

def correct_ocr_text(text: str) -> str:
    if not text: return text
    result = text
    for pattern, replacement in OCR_CORRECTIONS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def clean_cv_data(raw_data):
    cleaned_data = {}
    
    # Bước 1: Chuẩn hóa toàn bộ text TRƯỚC KHI lọc để sửa các chữ bị OCR đọc sai
    raw_level = correct_ocr_text(raw_data.get('level', '').strip())
    raw_position = correct_ocr_text(raw_data.get('position', '').strip())
    raw_address = correct_ocr_text(raw_data.get('address', '').strip())

    # Bước 2: Lọc và dồn lại nhãn
    final_level = raw_level if _has_level(raw_level) else ''
    final_address = raw_address if _has_address(raw_address) else ''
    final_position = raw_position if _has_position(raw_position) or (not _has_address(raw_position) and not _has_level(raw_position)) else ''

    leftover = []
    if not final_level and raw_level: leftover.append(raw_level)
    if not final_address and raw_address: leftover.append(raw_address)
    if not final_position and raw_position: leftover.append(raw_position)

    for text in leftover:
        lower = text.lower()
        if _has_address(text) and _has_position(text):
            split_idx = len(text)
            for kw in ADDRESS_KEYWORDS:
                idx = lower.find(kw)
                if idx != -1 and idx < split_idx: split_idx = idx
            part_pos, part_addr = text[:split_idx].strip(), text[split_idx:].strip()
            if part_pos and not final_position: final_position = part_pos
            if part_addr and not final_address: final_address = part_addr
        elif _has_level(text) and not final_level: final_level = text
        elif _has_address(text) and not final_address: final_address = text
        elif _has_position(text) and not final_position: final_position = text
        else:
            if not final_position: final_position = text

    # Bước 3: Gán lại và sửa lỗi từ điển
    raw_gpa = raw_data.get('gpa', '')
    gpa_match = re.search(r'(\d+[.,]\d+)', raw_gpa)
    
    # Lọc lấy từ khóa chính xác cho Level và xóa nó khỏi Position nếu bị trùng
    extracted_level = final_level
    found_lvl_word = None
    
    # Tìm level trong final_level, nếu trống thì tìm ké trong final_position
    search_text = final_level if final_level else final_position
    
    if search_text:
        for lvl in KNOWN_LEVELS:
            if re.search(rf'\b{lvl}\b', search_text, re.IGNORECASE):
                found_lvl_word = lvl
                extracted_level = lvl.capitalize()
                if extracted_level == 'Mid': extracted_level = 'Middle'
                break
                
    if found_lvl_word:
        # Xóa chữ đó (VD: "Senior") khỏi Position để tránh lặp (VD: "Senior Game Dev" -> "Game Dev")
        final_position = re.sub(rf'\b{found_lvl_word}\b', '', final_position, flags=re.IGNORECASE).strip()
        final_position = re.sub(r'^[-,\s]+', '', final_position) # Xóa gạch ngang hoặc khoảng trắng thừa ở đầu
                
    cleaned_data['level'] = extracted_level
    cleaned_data['position'] = final_position
    cleaned_data['address'] = final_address
    cleaned_data['gpa'] = gpa_match.group(1).replace(',', '.') if gpa_match else '0'
    cleaned_data['skill'] = correct_ocr_text(' '.join(raw_data.get('skill', '').split()))

    return cleaned_data

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
        raw_text_data = extract_text_from_images(img_paths, ocr_model)
        
        # 2. Xử lý dọn dẹp nhãn và sửa lỗi chính tả (CLEAN)
        cleaned_text_data = clean_cv_data(raw_text_data)

        print("\n--- 🔴 DỮ LIỆU THÔ TỪ OCR (RAW) ---")
        print(json.dumps(raw_text_data, ensure_ascii=False, indent=4))
        
        print("\n--- 🟢 DỮ LIỆU ĐÃ LỌC & SỬA LỖI (CLEANED) ---")
        print(json.dumps(cleaned_text_data, ensure_ascii=False, indent=4))
        print("="*60 + "\n")