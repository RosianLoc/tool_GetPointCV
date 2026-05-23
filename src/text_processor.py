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
    r'\benginer\b': 'engineer', r'\bengineer\b': 'engineer', r'\bsEngineer\b': 'Engineer', r'\bAENGINEER\b': 'AI ENGINEER',
    r'\bdeveloer\b': 'developer', r'\bdevelper\b': 'developer', r'\bUevelope\b': 'Developer', r'\bDevelope\b': 'Developer', r'\beveloper\b': 'developer',
    r'\bdesigher\b': 'designer', r'\bfronend\b': 'frontend', r'\bfrontnd\b': 'frontend', r'\bbacknd\b': 'backend', r'\bfullstck\b': 'fullstack', r'\bACKEND\b': 'BACKEND',
    r'\bomputer\b': 'Computer', r'\bT Suor\b': 'IT Support', r'\bstrator\b': 'Administrator', r'\bDevOr\b': 'DevOps', r'\bARC\b': 'ARCHITECT',
    r'\bsenoir\b': 'senior', r'\bjunoir\b': 'junior', r'\bSunior\b': 'Junior', r'\bsenor\b': 'senior', r'\bjunor\b': 'junior',
    r'\bfreshr\b': 'fresher', r'\bfreshe\b': 'fresher', r'\bintrn\b': 'intern', r'\bIntem\b': 'Intern', r'\bInter\b': 'Intern', r'\bnter\b': 'Intern', r'\bmidl\b': 'middle', r'\bFresner\b': 'Fresher', r'\bMIDDI\b': 'MIDDLE', r'\bINTE\b': 'INTERN', r'\bNTERN\b': 'INTERN',
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
    r'\bSogeMaker\b': 'SageMaker', r'\bSagemaker\b': 'SageMaker',
    r'\bUi/UxX\b': 'UI/UX', r'\bAPl\b': 'API', r'\bCommunicationProtocols\b': 'Communication Protocols',
    r'\bScikit-leam\b': 'Scikit-learn', r'\bLeaming\b': 'Learning', r'\bLeaming Algorithms\b': 'Learning Algorithms', r'\bLecrning\b': 'Learning', r'\bscikit-leorn\b': 'scikit-learn',
    r'\bNoturol Longuage\b': 'Natural Language', r'\bmotplotlib\b': 'matplotlib', r'\bWindow Server\b': 'Windows Server',
    
    # Lỗi Kỹ năng mềm & Các trường khác
    r'\bKy năng\b': 'Kỹ năng', r'\bK năng\b': 'Kỹ năng', r'\bK näng\b': 'Kỹ năng', r'\bKý näng\b': 'Kỹ năng', r'\bKy näng\b': 'Kỹ năng',
    r'\bK NNG\b': 'Kỹ năng', r'\bK NĂng\b': 'Kỹ năng', r'\bKY NANG\b': 'Kỹ năng', r'\bKỸ NĂNG\b': 'Kỹ năng', r'\bK NĂNG\b': 'Kỹ năng', r'K NĂNG': 'Kỹ năng',
    r'\bKnăng mm\b': 'Kỹ năng mềm', r'\bC8ng cu\b': 'Công cụ', r'\bcơ bàn\b': 'cơ bản', r'\bcơ bân\b': 'cơ bản', r'\bvði\b': 'với', r'\bhiu\b': 'hiểu',
    r'\bLàm vic nhóm\b': 'Làm việc nhóm', r'\blānh đgo nhóm\b': 'Lãnh đạo nhóm', r'\bqun lý thi gian\b': 'Quản lý thời gian', r'\bquan lý thi gian\b': 'Quản lý thời gian', r'\bThé thao\b': 'Thể thao',
    r'\bChuyanngann\b': 'Chuyên ngành', r'\bChuyenngann\b': 'Chuyên ngành', r'\bhuyenngann\b': 'Chuyên ngành',
    r'\bCưnnan\b': 'Chuyên ngành', r'\bCưnnan Knoα noc\b': 'Chuyên ngành Khoa học',
    r'\bD án tótnahi8r\b': 'Đồ án tốt nghiệp', r'\bDi án tót nabi8\b': 'Đồ án tốt nghiệp',
    r'\bĐ án tt nohié\b': 'Đồ án tốt nghiệp', r'\bĐ án tt nohié.\b': 'Đồ án tốt nghiệp',
    
    # Lỗi Địa chỉ, Thành phố, Quốc gia
    r'\bThành ph H ChrMinh\b': 'Thành phố Hồ Chí Minh', r'\bThành ph H Ch Minh\b': 'Thành phố Hồ Chí Minh', r'\bThnh ph H Chl Minh\b': 'Thành phố Hồ Chí Minh',
    r'\bThành phó H ChrMinh\b': 'Thành phố Hồ Chí Minh', r'\bThnh phó H ChrMinh\b': 'Thành phố Hồ Chí Minh', r'\bThành phH Chl Minh\b': 'Thành phố Hồ Chí Minh',
    r'\bThnh ph H Chr Minh\b': 'Thành phố Hồ Chí Minh', r'\bthành ph H Chl Minh\b': 'Thành phố Hồ Chí Minh', r'\bThnh ph H\b': 'Thành phố Hồ Chí Minh', r'\bThành phó H Ch\(Minh\b': 'Thành phố Hồ Chí Minh',
    r'\bH8 Chí Minh\b': 'Hồ Chí Minh', r'\bH ChrMinh\b': 'Hồ Chí Minh', r'\bH Chr Minh\b': 'Hồ Chí Minh', r'\bH Chl Minh\b': 'Hồ Chí Minh',
    r'\bH ChíMinh\b': 'Hồ Chí Minh', r'\bH Chi Minh\b': 'Hồ Chí Minh', r'\bH Chí Minh\b': 'Hồ Chí Minh', r'\bHo ChiMinh\b': 'Hồ Chí Minh', r'\bH Chí Minl\b': 'Hồ Chí Minh',
    r'\bHb ChT Minh\b': 'Hồ Chí Minh', r'\bHb Cht Minh\b': 'Hồ Chí Minh', r'\bThành phó Ho Chi Minh\b': 'Thành phố Hồ Chí Minh', r'\bThnh phó H Ch\(Minh\b': 'Thành phố Hồ Chí Minh',
    r'\bVit Nam\b': 'Việt Nam', r'\bViBt Nam\b': 'Việt Nam', r'\bViBt Nom\b': 'Việt Nam', r'\bViêt Nam\b': 'Việt Nam', r'\bVi8t Nam\b': 'Việt Nam', r'\bViet Nam\b': 'Việt Nam', r'\bVigt Nam\b': 'Việt Nam',
    r'\bPhưng\b': 'Phường', r'\bPhưòng\b': 'Phường', r'\bQun\b': 'Quận', r'\bQuġn\b': 'Quận', r'\bquiw Qun\b': 'Quận', r'\bQuàn\b': 'Quận',
    r'\bTn Phú\b': 'Tân Phú', r'\bTân Ph\b': 'Tân Phú', r'\bTn Phù\b': 'Tân Phú', r'\bTn Binh\b': 'Tân Bình', r'\bPh Nhun\b': 'Phú Nhuận', r'\bPhú Nhun\b': 'Phú Nhuận', r'\bTän Phú\b': 'Tân Phú', r'\bTn Ph\b': 'Tân Phú', r'\bTn Bnh\b': 'Tân Bình', r'\bTan Phu\b': 'Tân Phú',
    r'\bPh Thαnh\b': 'Phú Thạnh', r'\bHa Thơnh\b': 'Hòa Thạnh', r'\bHm\b': 'Hẻm', r'\bPhú Thnh\b': 'Phú Thạnh', r'\bPhú Thanh\b': 'Phú Thạnh', r'\bHa Thnh\b': 'Hòa Thạnh',
    r'\bBa Đinh\b': 'Ba Đình', r'\bHà Ni\b': 'Hà Nội', r'\bHà Ng\b': 'Hà Nội', r'\bHóc Mn\b': 'Hóc Môn', r'\bTh Đc\b': 'Thủ Đức', r'\bĐng Đa\b': 'Đống Đa', r'\bTy H\b': 'Tây Hồ', r'\bHon Kim\b': 'Hoàn Kiếm', r'\bG Vp\b': 'Gò Vấp',
    r'\bLB Ngā\b': 'Lê Ngã', r'\bĐng Vn Ngư\b': 'Đặng Văn Ngữ', r'\bĐng Văn Ng\b': 'Đặng Văn Ngữ', r'\b7Hong Xun Nhi\b': '7 Hoàng Xuân Nhị', r'\bLe Niğm\b': 'Lê Niệm', r'\bHunh Vn Bnh\b': 'Huỳnh Văn Bánh', r'\bLūy Bn Bích\b': 'Lũy Bán Bích',
    r'\bqun\b': 'quan', r'\bquan\b': 'quan', r'\bh chi minh\b': 'ho chi minh', r'\bh\.chi minh\b': 'ho chi minh', r'\bhcm\b': 'ho chi minh', r'\btp\.hcm\b': 'ho chi minh', r'\bMlnh\b': 'Minh',
    r'\bha noi\b': 'ha noi', r'\bhn\b': 'ha noi', r'\bphuong\b': 'phuong', r'\bduong\b': 'duong',
    r'\bSeniorCybersecurity\b': 'Senior Cybersecurity', r'\bKhu Phó\b': 'Khu Phố', r'\bCách Mang\b': 'Cách Mạng',
    r'\bChl Minh\b': 'Chí Minh', r'\bquiw\b': '', r'\bHin Vương\b': 'Hiền Vương', r'\bHin Vưdng\b': 'Hiền Vương', r'\byui\b': '',
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
    'cybersecurity', 'network', 'cloud', 'qa', 'tester', 'testing',
    'mobile', 'web', 'game', 'database', 'security', 'infrastructure',
    'sre', 'platform', 'product', 'project', 'technical', 'tech',
    'ml', 'machine learning', 'deep learning', 'ai', 'scientist',
]
KNOWN_LEVELS = ['intern', 'fresher', 'junior', 'middle', 'mid', 'senior', 'lead', 'manager']

# Các tiêu đề section mà CV thường dùng → cần xóa khỏi nội dung trích xuất
SECTION_HEADERS = [
    r'kỹ năng', r'ky nang', r'k nng', r'k năng', r'kỹ năng chuyên môn',
    r'K NĂNG', r'KỸ NĂNG', r'Kỹ năng',
    r'chuyên ngành', r'chuyên ngành khoa học',
    r'học vấn', r'kinh nghiệm', r'mục tiêu', r'thông tin cá nhân',
    r'kỹ năng mềm', r'kỹ năng cứng', r'skills', r'education',
    r'Cưnnan Knoα noc', r'cưnnan Knoa n',
]


def _strip_section_headers(text):
    """Xóa các tiêu đề section CV (Kỹ Năng, Chuyên ngành, ...) khỏi text."""
    result = text
    for header in SECTION_HEADERS:
        result = re.sub(header, '', result, flags=re.IGNORECASE)
    # Dọn các ký tự rác thừa sau khi xóa header
    result = re.sub(r'^[\s•\-:,;|]+', '', result)
    result = re.sub(r'\s{2,}', ' ', result).strip()
    return result


def _strip_phone_numbers(text):
    """Xóa số điện thoại Việt Nam khỏi text (0xxx, +84xxx, ...)."""
    # Pattern: 09xx, 03xx, 07xx, 08xx, 05xx, +84... (8-11 số)
    result = re.sub(r'(\+84|0)\d{8,10}', '', text)
    result = re.sub(r'\s{2,}', ' ', result).strip()
    return result


def _strip_birth_year(text):
    """Xóa năm sinh (4 chữ số đứng riêng lẻ, 19xx hoặc 20xx) khỏi text."""
    result = re.sub(r'\b(19|20)\d{2}\b', '', text)
    result = re.sub(r'\s{2,}', ' ', result).strip()
    return result


def _strip_orphan_chars(text, position='both'):
    """
    Xóa các ký tự lẻ loi (1-2 ký tự) bị lẹm từ YOLO box lân cận,
    thường nằm ở đầu hoặc cuối chuỗi.
    Ví dụ: "r DevOps Engineering" → "DevOps Engineering"
    Ví dụ: "rWeb Development" → "Web Development"
    Ví dụ: "Senior C" → "Senior"
    """
    if not text:
        return text
    result = text
    
    if position in ('start', 'both'):
        # Case 1: 1-2 ký tự thường + khoảng trắng + chữ hoa
        # Ví dụ: "r DevOps" → "DevOps"
        result = re.sub(r'^[a-z]{1,2}\s+(?=[A-Z])', '', result)
        
        # Case 2: 1-2 ký tự thường DÍNH LIỀN chữ hoa (không có space)
        # Ví dụ: "rWeb Development" → "Web Development"
        result = re.sub(r'^[a-z]{1,2}(?=[A-Z][a-z])', '', result)
    
    if position in ('end', 'both'):
        # Xóa 1-2 ký tự lẻ ở cuối chuỗi (sau khoảng trắng)
        result = re.sub(r'\s+[a-zA-Z]{1,2}$', '', result)
    
    return result.strip()


def _strip_urls_emails(text):
    """Xóa URL (facebook, linkedin, ...) và email khỏi text."""
    # Xóa URLs
    result = re.sub(r'https?://\S+', '', text)
    result = re.sub(r'(?:facebook|linkedin|github|gitlab|twitter|instagram)\.com\S*', '', result, flags=re.IGNORECASE)
    result = re.sub(r'\b\S+\.com\S*', '', result)
    # Xóa emails
    result = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '', result)
    result = re.sub(r'\s{2,}', ' ', result).strip()
    return result


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

    # Gom dữ liệu từ tất cả các key có chung tiền tố (vd: address_1, address_2 -> address)
    raw_level_texts = []
    raw_position_texts = []
    raw_address_texts = []
    raw_gpa_texts = []
    raw_skill_texts = []

    for k, v in raw_data.items():
        k_lower = k.lower()
        if k_lower.startswith('level'):
            raw_level_texts.append(v)
        elif k_lower.startswith('position'):
            raw_position_texts.append(v)
        elif k_lower.startswith('address'):
            raw_address_texts.append(v)
        elif k_lower.startswith('gpa'):
            raw_gpa_texts.append(v)
        elif k_lower.startswith('skill'):
            raw_skill_texts.append(v)

    # Tiền xử lý chữ và nối các text lại với nhau
    raw_level    = correct_ocr_text(' '.join(raw_level_texts).strip())
    raw_position = correct_ocr_text(' '.join(raw_position_texts).strip())
    raw_address  = correct_ocr_text(' '.join(raw_address_texts).strip())

    # Xóa URL/email khỏi tất cả
    raw_level    = _strip_urls_emails(raw_level)
    raw_position = _strip_urls_emails(raw_position)
    raw_address  = _strip_urls_emails(raw_address)

    # Xóa SĐT khỏi address (OCR hay đọc chung SĐT vào address)
    raw_address = _strip_phone_numbers(raw_address)
    # Xóa năm sinh (2005, 1999, ...) bị lẫn vào address
    raw_address = _strip_birth_year(raw_address)

    # Xóa ký tự lẻ bị lẹm viền ở đầu/cuối level và position
    raw_level    = _strip_orphan_chars(raw_level, 'end')    # Level hay bị lẹm cuối: "Senior C"
    raw_position = _strip_orphan_chars(raw_position, 'start')  # Position hay bị lẹm đầu: "r DevOps"

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
        
        # Nếu final_level có chứa text khác ngoài chữ level (ví dụ YOLO gộp nhầm Intern và Position)
        # Thì sau khi lấy được 'Intern', ta ném phần chữ còn lại sang cho position.
        remaining_level_text = re.sub(rf'\b{found_lvl_word}\b', '', final_level, flags=re.IGNORECASE).strip()
        remaining_level_text = re.sub(r'^[-,\s]+', '', remaining_level_text)
        # Xóa ký tự lẻ khỏi phần remaining (có thể là ký tự lẹm viền)
        remaining_level_text = _strip_orphan_chars(remaining_level_text, 'both')
        if remaining_level_text and remaining_level_text.lower() not in final_position.lower():
            final_position = (final_position + " " + remaining_level_text).strip()
    
    # Dọn rác lần cuối cho position (xóa ký tự lẻ còn sót)
    final_position = _strip_orphan_chars(final_position, 'both')
    # Xóa SĐT nếu lọt vào position
    final_position = _strip_phone_numbers(final_position)
                
    cleaned_data['level']    = extracted_level
    cleaned_data['position'] = final_position
    cleaned_data['address']  = final_address

    # --- BƯỚC 3: GPA & SKILL ---
    raw_gpa = ' '.join(raw_gpa_texts)
    gpa_match = re.search(r'(\d+[.,]\d+)', raw_gpa)
    cleaned_data['gpa'] = gpa_match.group(1).replace(',', '.') if gpa_match else '0'

    raw_skill = ' '.join(raw_skill_texts)
    cleaned_skill = correct_ocr_text(' '.join(raw_skill.split()))
    # Xóa section header "Kỹ Năng" khỏi nội dung skill
    cleaned_skill = _strip_section_headers(cleaned_skill)
    # Xóa bullet points • thừa
    cleaned_skill = re.sub(r'[•·]', ' ', cleaned_skill)
    cleaned_skill = re.sub(r'\s{2,}', ' ', cleaned_skill).strip()

    # --- BƯỚC 3b: FALLBACK GPA ---
    # Khi YOLO gộp vùng Education/GPA vào box skill (hay gặp ở CV tiếng Anh),
    # GPA text bị chôn trong skill. Cần scan skill (và các field khác) để cứu GPA.
    if cleaned_data['gpa'] == '0':
        # Các pattern GPA phổ biến (hỗ trợ cả EN và VN)
        gpa_patterns = [
            r'GPA\s*[:\-]?\s*(\d+[.,]\d+)\s*/\s*(?:4(?:\.0)?|10)',  # GPA:3.8/4, GPA: 3.8/4.0
            r'CGPA\s*[:\-]?\s*(\d+[.,]\d+)\s*/\s*(?:4(?:\.0)?|10)',  # CGPA:3.8/4
            r'GPA\s*[:\-]?\s*(\d+[.,]\d+)',                          # GPA:3.8, GPA: 3.8
            r'CGPA\s*[:\-]?\s*(\d+[.,]\d+)',                         # CGPA:3.8
            r'(\d+[.,]\d+)\s*/\s*4(?:\.0)?',                         # 3.8/4, 3.8/4.0
        ]
        
        # Scan tất cả các field để tìm GPA bị lạc
        all_texts_to_scan = [
            ('skill', cleaned_skill),
            ('address', final_address),
            ('position', final_position),
            ('level', extracted_level),
        ]
        
        for field_name, field_text in all_texts_to_scan:
            if not field_text:
                continue
            for pattern in gpa_patterns:
                match = re.search(pattern, field_text, re.IGNORECASE)
                if match:
                    gpa_val = match.group(1).replace(',', '.')
                    # Validate: GPA phải trong khoảng hợp lệ (0.0 - 10.0)
                    try:
                        gpa_float = float(gpa_val)
                    except ValueError:
                        continue
                    if 0.0 < gpa_float <= 10.0:
                        cleaned_data['gpa'] = gpa_val
                        print(f"[FALLBACK GPA] Tim thay GPA={gpa_val} trong field '{field_name}'")
                        
                        # Nếu GPA nằm trong skill → xóa phần education/GPA khỏi skill
                        if field_name == 'skill':
                            # Xóa đoạn GPA (vd: "GPA:3.8/4", "GPA: 3.8/4.0")
                            cleaned_skill = re.sub(r'C?GPA\s*[:\-]?\s*\d+[.,]\d+\s*(?:/\s*(?:4(?:\.0)?|10))?\s*', '', cleaned_skill, flags=re.IGNORECASE)
                            # Xóa thông tin education hay bị gộp vào skill (university, major, ...)
                            education_noise_patterns = [
                                r'Major\s*:\s*\S+(?:\s+\S+){0,3}',          # Major:Information Technology
                                r'(?:Ho Chi Minh City|Ha Noi|Da Nang)?\s*(?:University|College|Institute)\s+(?:of\s+)?\S+(?:\s+\S+){0,5}(?:\(.*?\))?',  # Ho Chi Minh City University of Technology (HCMUT)
                                r'(?:Bachelor|Master|B\.?S\.?|M\.?S\.?)\s+(?:of\s+)?\S+(?:\s+\S+){0,4}',  # Bachelor of Science in CS
                                r'\b\d{4}\s*[-–]\s*(?:\d{4}|Present|Nay)\b', # 2020 - Present, 2020 - 2024
                                r'\b\d{4}\s+Present\b',                      # 2020 Present
                                r'(?:Education|Hoc van|EDUCATION)\s*:?\s*',   # Section header Education
                            ]
                            for noise_pat in education_noise_patterns:
                                cleaned_skill = re.sub(noise_pat, '', cleaned_skill, flags=re.IGNORECASE)
                            # Dọn rác sau khi xóa
                            cleaned_skill = re.sub(r'\s{2,}', ' ', cleaned_skill).strip()
                            cleaned_skill = re.sub(r'^[\s,.\-;|]+|[\s,.\-;|]+$', '', cleaned_skill)
                        break
            if cleaned_data['gpa'] != '0':
                break

    cleaned_data['skill'] = cleaned_skill

    return cleaned_data

# --- TEST VỚI DỮ LIỆU ĐANG BỊ LỖI CỦA BẠN ---
if __name__ == "__main__":
    # Test case 1: Dữ liệu bị YOLO gán sai nhãn
    error_data = {
        "level": "atabase Engineer",
        "position": "Qun Tn Phú, H Chi Minh",
        "gpa": "3.1",
        "address": "Senior",
        "skill": "Cl/CD & Tđng ha AWS..."
    }
    
    print("=== TEST 1: YOLO gán sai nhãn ===")
    print("Dữ liệu gốc (Bị loạn):")
    print(json.dumps(error_data, ensure_ascii=False, indent=4))
    fixed_data = clean_cv_data(error_data)
    print("\nDữ liệu sau khi AI dọn dẹp lại:")
    print(json.dumps(fixed_data, ensure_ascii=False, indent=4))
    
    # Test case 2: Dữ liệu bị lẹm viền
    print("\n\n=== TEST 2: YOLO cắt lẹm viền ===")
    error_data_2 = {
        "level": "Senior C",
        "position": "r DevOps Engineering",
        "address": "0943009243 Qun 6, H ChíMinh",
        "gpa": "Cưnnan Knoα noc • GPA: 3.0/4.0 • Đ án tt nohié.",
        "skill": "K NNG Cl/CD Pipelines Automation and Deployment Tools Docker and Kubernetes •Linux System Administration SQL •Infrastructure os Code (laC) AWS (SogeMaker, EC2)"
    }
    
    print("Dữ liệu gốc (Bị lẹm viền):")
    print(json.dumps(error_data_2, ensure_ascii=False, indent=4))
    fixed_data_2 = clean_cv_data(error_data_2)
    print("\nDữ liệu sau khi AI dọn dẹp lại:")
    print(json.dumps(fixed_data_2, ensure_ascii=False, indent=4))

    # Test case 3: CV mới - rWeb dính liền, năm sinh 2005, K NĂNG header
    print("\n\n=== TEST 3: rWeb dính liền + năm sinh + K NĂNG ===")
    error_data_3 = {
        "level": "Senior",
        "position": "rWeb Development",
        "address": "2005 0943009243 Qun 7, H Chí Minh",
        "gpa": "cưnnan Knoa n • GPA:3.1/4.0 dé cohi",
        "skill": "K NĂNG HTML. CSS Responsive Web Design JavaScript Frontend and Backend Development SQL Infrastructure as Code (laC) RESTful APIs"
    }
    
    print("Dữ liệu gốc:")
    print(json.dumps(error_data_3, ensure_ascii=False, indent=4))
    fixed_data_3 = clean_cv_data(error_data_3)
    print("\nDữ liệu sau khi AI dọn dẹp lại:")
    print(json.dumps(fixed_data_3, ensure_ascii=False, indent=4))

    # Test case 4: Dữ liệu bị dính key _1
    print("\n\n=== TEST 4: Dữ liệu chứa key có hậu tố _1 ===")
    error_data_4 = {
        "address_1": "Qun 6, H Chi Minh",
        "gpa_1": "• GPA:3.0/4.0",
        "level_1": "Senior",
        "position_1": "DevOps Engineering",
        "skill_1": "K NĂNG Cl/CD Pipelines Automation and Deployment Tools Docker and Kubernetes Linux System Administration SQL •Infrastructure as Code (laC) AWS (SogeMaker, EC2)"
    }
    
    print("Dữ liệu gốc:")
    print(json.dumps(error_data_4, ensure_ascii=False, indent=4))
    fixed_data_4 = clean_cv_data(error_data_4)
    print("\nDữ liệu sau khi AI dọn dẹp lại:")
    print(json.dumps(fixed_data_4, ensure_ascii=False, indent=4))