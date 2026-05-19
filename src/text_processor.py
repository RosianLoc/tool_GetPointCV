import re
import json

# ================================================================
# TỪ ĐIỂN SỬa LỖI OCR PHỔ BIẾN CHO CV IT
# Key = lỗi OCR hay gặp, Value = từ đúng
# ================================================================
OCR_CORRECTIONS = {
    # Lỗi vị trí, cấp bậc
    r'\bsyster\b': 'system', r'\bsytem\b': 'system', r'\bsysem\b': 'system',
    r'\badministrato\b': 'administrator', r'\badministrat\b': 'administrator', r'\badministrtor\b': 'administrator',
    r'\benginer\b': 'engineer', r'\bengineer\b': 'engineer', r'\bsEngineer\b': 'Engineer',
    r'\bdeveloer\b': 'developer', r'\bdevelper\b': 'developer', r'\bUevelope\b': 'Developer', r'\bDevelope\b': 'Developer',
    r'\bdesigher\b': 'designer', r'\bfronend\b': 'frontend', r'\bfrontnd\b': 'frontend', r'\bbacknd\b': 'backend', r'\bfullstck\b': 'fullstack',
    r'\bsenoir\b': 'senior', r'\bjunoir\b': 'junior', r'\bSunior\b': 'Junior', r'\bsenor\b': 'senior', r'\bjunor\b': 'junior',
    r'\bfreshr\b': 'fresher', r'\bfreshe\b': 'fresher', r'\bintrn\b': 'intern', r'\bIntem\b': 'Intern', r'\bInter\b': 'Intern', r'\bnter\b': 'Intern', r'\bmidl\b': 'middle',
    r'\bAl Engineer\b': 'AI Engineer',
    
    # Lỗi ngôn ngữ / công nghệ
    r'\blava\b': 'java', r'\bjave\b': 'java',
    r'\bjavascrint\b': 'javascript', r'\bjavascrit\b': 'javascript', r'\bjavascritp\b': 'javascript',
    r'\btypescrit\b': 'typescript', r'\bpythn\b': 'python', r'\bpytohn\b': 'python',
    r'\breact\.js\b': 'reactjs', r'\breactis\b': 'reactjs', 
    r'\bnode\.js\b': 'nodejs', r'\bnodeis\b': 'nodejs', r'\bvue\.js\b': 'vuejs', r'\bangulr\b': 'angular', r'\bnestis\b': 'nestjs',
    r'\blarave\b': 'laravel', r'\bspringboot\b': 'spring boot', r'\bdjang\b': 'django',
    r'\bcl/cd\b': 'ci/cd', r'\bc1/cd\b': 'ci/cd', r'\bcicd\b': 'ci/cd', r'\bci\\cd\b': 'ci/cd',
    r'\bdockr\b': 'docker', r'\bkuberntes\b': 'kubernetes', r'\bk8s\b': 'kubernetes', r'\bterrafom\b': 'terraform', r'\bjenkin\b': 'jenkins',
    r'\bmongdb\b': 'mongodb', r'\bpostgres\b': 'postgresql', r'\bmysq\b': 'mysql', r'\bredis\b': 'redis',
    r'\bgitub\b': 'github', r'\bgitab\b': 'gitlab', r'\bfigm\b': 'figma', r'\blinx\b': 'linux', r'\bwindws\b': 'windows', r'\bpowershel\b': 'powershell',
    r'\bsowae\b': 'software', r'\bsoftwar\b': 'software', r'\bsofware\b': 'software', r'\bsoftare\b': 'software', r'\bsoftwaer\b': 'software',
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

def correct_ocr_text(text: str) -> str:
    """Sửa lỗi OCR bằng từ điển, giữ nguyên case gốc."""
    if not text:
        return text
    result = text
    for pattern, replacement in OCR_CORRECTIONS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


ADDRESS_KEYWORDS = [
    'quận', 'qun', 'q.', 'phố', 'hồ chí minh', 'ho chi minh', 'h chi minh',
    'hà nội', 'ha noi', 'hcm', 'tp.hcm', 'thành phố', 'thanh pho',
    'phường', 'phuong', 'đường', 'duong', 'tỉnh', 'district', 'city', 'street',
    'quận 1', 'quận 2', 'quận 3', 'quận 4', 'quận 5', 'quận 6', 'quận 7',
    'việt nam', 'viet nam', 'vi8t nam', 'thanh phó', 'hó chl minh', 'hó chi minh'
]
POSITION_KEYWORDS = [
    'engineer', 'developer', 'designer', 'manager', 'analyst',
    'lead', 'architect', 'devops', 'frontend', 'backend', 'fullstack',
    'software', 'system', 'data', 'kỹ sư', 'lập trình',
]
KNOWN_LEVELS = ['intern', 'fresher', 'junior', 'middle', 'mid', 'senior', 'lead', 'manager']


def _has_address(text):
    t = text.lower()
    return any(kw in t for kw in ADDRESS_KEYWORDS)

def _has_position(text):
    t = text.lower()
    return any(kw in t for kw in POSITION_KEYWORDS)

def _has_level(text):
    return any(lvl in text.lower().split() for lvl in KNOWN_LEVELS)


def clean_cv_data(raw_data):
    cleaned_data = {}

    # BƯỚC 1: Chuẩn hóa chữ bị OCR đọc sai TRƯỚC KHI lọc
    raw_level    = correct_ocr_text(raw_data.get('level', '').strip())
    raw_position = correct_ocr_text(raw_data.get('position', '').strip())
    raw_address  = correct_ocr_text(raw_data.get('address', '').strip())

    # --- BƯỚC 2: TIN TƯỜNG YOLO TRƯỚC ---
    # Nếu YOLO gán đúng nhãn thì dùng thẳng, không cần pool
    final_level    = raw_level    if _has_level(raw_level)    else ''
    final_address  = raw_address  if _has_address(raw_address) else ''
    final_position = raw_position if _has_position(raw_position) or \
                     (not _has_address(raw_position) and not _has_level(raw_position)) else ''

    # --- BƯỚC 2: XỬ LÝ CÁC TRƯỜNG Bị YOLO GÁN SAI NHÃN ---
    # Gom các trường chưa được gán vào pool để phân loại lại
    leftover = []
    if not final_level and raw_level:
        leftover.append(raw_level)
    if not final_address and raw_address:
        leftover.append(raw_address)
    if not final_position and raw_position:
        leftover.append(raw_position)

    for text in leftover:
        # Tách nếu 1 chuỗi chứa cả 2 loại
        lower = text.lower()
        if _has_address(text) and _has_position(text):
            split_idx = len(text)
            for kw in ADDRESS_KEYWORDS:
                idx = lower.find(kw)
                if idx != -1 and idx < split_idx:
                    split_idx = idx
            part_pos  = text[:split_idx].strip()
            part_addr = text[split_idx:].strip()
            if part_pos  and not final_position: final_position = part_pos
            if part_addr and not final_address:  final_address  = part_addr
        elif _has_level(text)   and not final_level:    final_level    = text
        elif _has_address(text) and not final_address:  final_address  = text
        elif _has_position(text) and not final_position: final_position = text
        else:
            # Không nhận diện được → gán vào position nếu chưa có
            if not final_position: final_position = text

    # Lọc lấy từ khóa chính xác cho Level và xóa nó khỏi Position nếu bị trùng
    extracted_level = final_level
    found_lvl_word = None
    
    search_text = final_level if final_level else final_position
    
    if search_text:
        for lvl in KNOWN_LEVELS:
            if re.search(rf'\b{lvl}\b', search_text, re.IGNORECASE):
                found_lvl_word = lvl
                extracted_level = lvl.capitalize()
                if extracted_level == 'Mid': extracted_level = 'Middle'
                break
                
    if found_lvl_word:
        final_position = re.sub(rf'\b{found_lvl_word}\b', '', final_position, flags=re.IGNORECASE).strip()
        final_position = re.sub(r'^[-,\s]+', '', final_position)
                
    cleaned_data['level']    = extracted_level
    cleaned_data['position'] = final_position
    cleaned_data['address']  = final_address

    # --- BƯỚC 3: GPA & SKILL ---
    raw_gpa = raw_data.get('gpa', '')
    gpa_match = re.search(r'(\d+[.,]\d+)', raw_gpa)
    cleaned_data['gpa'] = gpa_match.group(1).replace(',', '.') if gpa_match else '0'

    raw_skill = raw_data.get('skill', '')
    cleaned_data['skill'] = correct_ocr_text(' '.join(raw_skill.split()))

    return cleaned_data

# --- TEST VỚI DỮ LIỆU ĐANG BỊ LỖI CỦA BẠN ---
if __name__ == "__main__":
    error_data = {
        "level": "atabase Engineer",
        "position": "Qun Tn Phú, H Chi Minh",
        "gpa": "3.1",
        "address": "Senior",
        "skill": "Cl/CD & Tđng ha AWS..."
    }
    
    print("Dữ liệu gốc (Bị loạn):")
    print(json.dumps(error_data, ensure_ascii=False, indent=4))
    
    fixed_data = clean_cv_data(error_data)
    
    print("\nDữ liệu sau khi AI dọn dẹp lại:")
    print(json.dumps(fixed_data, ensure_ascii=False, indent=4))