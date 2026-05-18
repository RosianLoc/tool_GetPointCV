import re
import json

# ================================================================
# TỪ ĐIỂN SỬa LỖI OCR PHỔ BIẾN CHO CV IT
# Key = lỗi OCR hay gặp, Value = từ đúng
# ================================================================
OCR_CORRECTIONS = {
    # === LỖI TỪ ẢNH THỰC TẾC (thấy trong demo) ===
    r'\bsyster\b': 'system',
    r'\bsytem\b': 'system',       r'\bsysem\b': 'system',
    r'\badministrato\b': 'administrator', r'\badministrat\b': 'administrator',
    r'\badministrtor\b': 'administrator',
    r'\blava\b': 'java',          r'\bjave\b': 'java',
    r'\bjavascrint\b': 'javascript', r'\bjavascrit\b': 'javascript',
    r'\bjavascritp\b': 'javascript',
    r'\bqun\b': 'quan',           r'\bquan\b': 'quan',
    r'\bh chi minh\b': 'ho chi minh', r'\bh\.chi minh\b': 'ho chi minh',
    r'\bhcm\b': 'ho chi minh',    r'\btp\.hcm\b': 'ho chi minh',
    r'\bha noi\b': 'ha noi',      r'\bhn\b': 'ha noi',
    r'\bphuong\b': 'phuong',      r'\bduong\b': 'duong',

    # === LỖI KÝ TỰ PHỔ BIẾN ===
    # Software / Engineer
    r'\bsowae\b': 'software',     r'\bsoftwar\b': 'software',
    r'\bsofware\b': 'software',   r'\bsoftare\b': 'software',
    r'\bsoftwaer\b': 'software',
    r'\benginer\b': 'engineer',   r'\bengineer\b': 'engineer',
    r'\bengineer\b': 'engineer',  r'\bengineer\b': 'engineer',
    # Developer / Designer
    r'\bdeveloer\b': 'developer', r'\bdevelper\b': 'developer',
    r'\bdesigher\b': 'designer',  r'\bdesiger\b': 'designer',
    # Frontend / Backend / Fullstack
    r'\bfronend\b': 'frontend',   r'\bfrontnd\b': 'frontend',
    r'\bbacknd\b': 'backend',     r'\bbackend\b': 'backend',
    r'\bfullstck\b': 'fullstack', r'\bfullstac\b': 'fullstack',
    # Languages
    r'\bjavascrit\b': 'javascript', r'\bjavascript\b': 'javascript',
    r'\btypescrit\b': 'typescript', r'\btypescript\b': 'typescript',
    r'\bpythn\b': 'python',       r'\bpytohn\b': 'python',
    r'\bphp\b': 'php',
    # Frameworks
    r'\breact\.js\b': 'reactjs',  r'\breactis\b': 'reactjs',
    r'\bnode\.js\b': 'nodejs',    r'\bnodeis\b': 'nodejs',
    r'\bvue\.js\b': 'vuejs',      r'\bvueis\b': 'vuejs',
    r'\bangulr\b': 'angular',     r'\bnestis\b': 'nestjs',
    r'\blarave\b': 'laravel',     r'\bdjang\b': 'django',
    r'\bspringboot\b': 'spring boot',
    # DevOps / Cloud
    r'\bcl/cd\b': 'ci/cd',        r'\bc1/cd\b': 'ci/cd',
    r'\bci\\cd\b': 'ci/cd',       r'\bcicd\b': 'ci/cd',
    r'\bdockr\b': 'docker',       r'\bkuberntes\b': 'kubernetes',
    r'\bk8s\b': 'kubernetes',     r'\bjenkin\b': 'jenkins',
    r'\bterrafom\b': 'terraform',
    # DB
    r'\bmongdb\b': 'mongodb',     r'\bpostgres\b': 'postgresql',
    r'\bmysq\b': 'mysql',         r'\bredis\b': 'redis',
    # Level
    r'\bsenoir\b': 'senior',      r'\bsenor\b': 'senior',
    r'\bjunoir\b': 'junior',      r'\bjunor\b': 'junior',
    r'\bfreshr\b': 'fresher',     r'\bfreshe\b': 'fresher',
    r'\bintrn\b': 'intern',       r'\bmidl\b': 'middle',
    # Tools
    r'\bgitub\b': 'github',       r'\bgitab\b': 'gitlab',
    r'\bfigm\b': 'figma',         r'\blinx\b': 'linux',
    r'\bwindws\b': 'windows',     r'\bpowershel\b': 'powershell',
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

    raw_level    = raw_data.get('level', '').strip()
    raw_position = raw_data.get('position', '').strip()
    raw_address  = raw_data.get('address', '').strip()

    # --- BƯỚC 1: TIN TƯỜNG YOLO TRƯỚC ---
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

    cleaned_data['level']    = final_level
    cleaned_data['position'] = final_position
    cleaned_data['address']  = final_address

    # --- BƯỚC 3: GPA & SKILL ---
    raw_gpa = raw_data.get('gpa', '')
    gpa_match = re.search(r'(\d+[.,]\d+)', raw_gpa)
    cleaned_data['gpa'] = gpa_match.group(1).replace(',', '.') if gpa_match else '0'

    raw_skill = raw_data.get('skill', '')
    cleaned_data['skill'] = correct_ocr_text(' '.join(raw_skill.split()))

    cleaned_data['position'] = correct_ocr_text(cleaned_data['position'])
    cleaned_data['level']    = correct_ocr_text(cleaned_data['level'])
    cleaned_data['address']  = correct_ocr_text(cleaned_data['address'])

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