"""
PDF Text Extractor — Bypass YOLO cho file PDF.
Đọc text trực tiếp từ PDF (text kỹ thuật số, không cần OCR)
rồi trích xuất các tech keywords riêng lẻ thay vì lấy nguyên dòng.

Hỗ trợ cả CV 1 cột và 2 cột.
"""
import re
import fitz  # PyMuPDF

# =========================================================
# DANH SÁCH KEYWORD
# =========================================================

ADDRESS_KEYWORDS_DETECT = [
    'quận', 'phường', 'đường', 'hồ chí minh', 'hà nội', 'đà nẵng',
    'tp.hcm', 'thành phố', 'tỉnh', 'việt nam', 'district', 'city',
    'street', 'ward', 'province', 'hẻm', 'khu phố',
    'tân phú', 'tân bình', 'bình thạnh', 'phú nhuận', 'gò vấp',
    'thủ đức', 'bình tân', 'hóc môn', 'ho chi minh',
    'ba diem', 'ba điểm', 'binh chanh', 'bình chánh',
]

POSITION_KEYWORDS_DETECT = [
    'engineer', 'developer', 'designer', 'manager', 'analyst',
    'architect', 'devops', 'frontend', 'backend', 'fullstack',
    'software', 'data scientist', 'data engineer', 'data analyst',
    'cybersecurity', 'network', 'cloud', 'qa', 'tester',
    'mobile', 'web developer', 'game', 'database', 'security',
    'machine learning', 'deep learning', 'ai engineer',
    'system administrator', 'helpdesk', 'it support', 'it /',
    'embedded', 'iot', 'blockchain', 'php developer',
    'intern', 'fresher', 'junior', 'senior',
]

LEVEL_KEYWORDS = ['intern', 'fresher', 'junior', 'middle', 'mid-level', 'senior', 'lead', 'manager', 'principal']

# ===== DANH SÁCH KỸ NĂNG CHÍNH XÁC (exact match, case-insensitive) =====
# Chỉ trích xuất đúng các TỪ KHÓA này, không lấy nguyên câu mô tả
TECH_SKILLS_EXACT = [
    # --- Dài trước, ngắn sau (tránh match ngắn trước rồi bỏ sót dài) ---
    # Networking & Security (multi-word)
    'Active Directory', 'Windows Server', 'Web Server', 'SQL Server',
    'RIP v2', 'TCP/IP',
    # Frameworks multi-word
    'React Native', 'Vue.js', 'Node.js', 'Next.js', 'Nuxt.js', 'Nest.js',
    'Express.js', 'Spring Boot', 'Ruby on Rails', 'ASP.NET',
    'Material UI', 'Adobe XD', 'Android Studio', 'Visual Studio', 'VS Code',
    'Unreal Engine', 'Three.js',
    'GitHub Actions', 'GitLab CI', 'Google Cloud',
    'REST API', 'RESTful API', 'Bash Script',
    # AI/ML multi-word
    'Machine Learning', 'Deep Learning', 'Computer Vision',
    'Design Pattern', 'Data Structures',
    # Soft skills multi-word
    'Problem Solving', 'Critical Thinking', 'Time Management',
    # Single-word skills
    'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#',
    'HTML5', 'HTML', 'CSS3', 'CSS', 'SCSS', 'SASS', 'PHP', 'Ruby', 'Rust', 'Golang',
    'Swift', 'Kotlin', 'Dart', 'MATLAB', 'Scala', 'Perl',
    'Bash', 'Shell', 'PowerShell', 'SQL', 'NoSQL',
    'React', 'ReactJS', 'Angular', 'AngularJS', 'Vue', 'VueJS',
    'NextJS', 'Svelte', 'NodeJS', 'Express', 'NestJS',
    'Django', 'Flask', 'FastAPI', 'Spring', 'Laravel', '.NET',
    'jQuery', 'Bootstrap', 'Tailwind', 'TailwindCSS',
    'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib',
    'Docker', 'Kubernetes', 'K8s', 'Jenkins', 'CI/CD',
    'AWS', 'Azure', 'GCP', 'Terraform', 'Ansible',
    'Nginx', 'Apache', 'Linux', 'Ubuntu', 'CentOS',
    'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
    'Oracle', 'SQLite', 'DynamoDB', 'Cassandra', 'Firebase',
    'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Jira', 'Confluence',
    'Figma', 'Photoshop', 'Illustrator', 'Sketch',
    'Postman', 'Swagger', 'GraphQL',
    'IntelliJ', 'Eclipse',
    'DNS', 'DHCP', 'FTP', 'SNMP', 'NAT', 'VPN',
    'RIP', 'OSPF', 'BGP', 'VLAN', 'Firewall', 'IDS', 'IPS',
    'ADDS', 'GPO', 'DFS', 'WDS', 'RRAS', 'NTFS',
    'VMware', 'VirtualBox', 'Hyper-V', 'GNS3', 'Zabbix', 'Nagios',
    'Cisco', 'MikroTik', 'pfSense', 'Wireshark',
    'Agile', 'Scrum', 'Kanban', 'OOP', 'SOLID',
    'NLP', 'Blockchain', 'Microservices',
    'API', 'SDK', 'XML', 'JSON', 'YAML',
    'Unity', 'Blender',
    'TOEIC', 'IELTS', 'Communication', 'Teamwork', 'Leadership',
]

SECTION_HEADERS = [
    r'\bskills?\b', r'\bkỹ năng\b', r'\bky năng\b',
    r'\beducation\b', r'\bhọc vấn\b',
    r'\bexperience\b', r'\bkinh nghiệm\b',
    r'\bproject\b', r'\bdự án\b',
    r'\bobjective\b', r'\bmục tiêu\b',
    r'\bcontact\b', r'\bliên hệ\b',
    r'\blanguages?\b', r'\bngôn ngữ\b',
    r'\bcertificat\b', r'\bchứng chỉ\b',
    r'\bhobbies?\b', r'\bsở thích\b',
    r'\breference\b', r'\btham khảo\b',
    r'\bsummary\b', r'\btóm tắt\b',
    r'\babout me\b', r'\bpersonal\b',
    r'\bachievement\b', r'\bthành tích\b',
    r'\bwork history\b', r'\bmonitoring\b',
]

# =========================================================


def extract_text_from_pdf(pdf_path: str) -> str:
    """Đọc toàn bộ text từ file PDF."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
    doc.close()
    return full_text.strip()


def _is_section_header(line: str) -> bool:
    """Kiểm tra xem dòng có phải tiêu đề section không."""
    line_stripped = line.strip()
    if not line_stripped or len(line_stripped) > 40:
        return False
    line_lower = line_stripped.lower()
    for header in SECTION_HEADERS:
        if re.search(header, line_lower, re.IGNORECASE):
            if len(line_stripped.split()) <= 5:
                return True
    return False


def _find_gpa(text: str) -> str:
    """Tìm GPA trong toàn bộ text."""
    patterns = [
        r'GPA\s*[:\-]?\s*(\d+[.,]\d+)\s*/\s*4\.0',
        r'GPA\s*[:\-]?\s*(\d+[.,]\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).replace(',', '.')
    return '0'


def _find_level(text: str) -> str:
    """Tìm Level/Cấp bậc trong text."""
    text_lower = text.lower()
    for lvl in LEVEL_KEYWORDS:
        if re.search(rf'\b{lvl}\b', text_lower):
            result = lvl.capitalize()
            if result == 'Mid-level':
                result = 'Middle'
            return result
    return ''


def _find_position(text: str) -> str:
    """Tìm Vị trí công việc trong text (thường ở phần đầu CV, dưới tên)."""
    lines = text.split('\n')
    
    # Tìm trong 15 dòng đầu tiên (nơi thường ghi tên + chức danh)
    for line in lines[:15]:
        line_stripped = line.strip()
        if not line_stripped or len(line_stripped) < 3 or len(line_stripped) > 60:
            continue
        line_lower = line_stripped.lower()
        
        if _is_section_header(line_stripped):
            continue
        
        for kw in POSITION_KEYWORDS_DETECT:
            if kw in line_lower:
                return line_stripped
    
    # Fallback: Tìm pattern "Level + Position"
    for lvl in LEVEL_KEYWORDS:
        pattern = rf'\b{lvl}\b\s+(.+?)(?:\n|$)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pos = match.group(0).strip()
            if len(pos) < 60:
                return pos
    
    return ''


def _find_address(text: str) -> str:
    """Tìm Địa chỉ trong text. Ghép các dòng ngắn liền kề nếu cần."""
    lines = text.split('\n')
    best_line = ''
    best_score = 0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped or len(line_stripped) < 3 or len(line_stripped) > 150:
            continue
        
        if _is_section_header(line_stripped):
            continue
        
        # Thử ghép dòng hiện tại với dòng kế tiếp (trường hợp địa chỉ nằm trên 2 dòng)
        combined = line_stripped
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and len(next_line) < 80:
                combined = line_stripped + ', ' + next_line
        
        line_lower = combined.lower()
        match_count = sum(1 for kw in ADDRESS_KEYWORDS_DETECT if kw in line_lower)
        
        if match_count > best_score:
            best_score = match_count
            # Nếu match nhiều hơn nhờ ghép 2 dòng thì dùng combined, ngược lại dùng dòng đơn
            single_score = sum(1 for kw in ADDRESS_KEYWORDS_DETECT if kw in line_stripped.lower())
            if single_score >= match_count:
                best_line = line_stripped
            else:
                best_line = combined
    
    if best_score >= 1:
        return best_line
    return ''


def _find_skills(text: str) -> str:
    """
    Trích xuất KỸ NĂNG từ PDF bằng cách tìm exact match các tech keywords.
    CHỈ lấy tên công nghệ/tool, KHÔNG lấy nguyên câu mô tả dự án.
    """
    text_lower = text.lower()
    found_skills = []
    
    for skill in TECH_SKILLS_EXACT:
        # Tìm skill trong text (case-insensitive)
        # Dùng word boundary để tránh match partial (vd: "C" không match trong "Cisco")
        skill_lower = skill.lower()
        
        # Với các skill ngắn (1-2 ký tự như C, R, Go), cần kiểm tra word boundary chặt hơn
        if len(skill) <= 2:
            # Chỉ match nếu là từ đứng độc lập (có dấu phân cách rõ ràng)
            pattern = rf'(?<![a-zA-Z]){re.escape(skill_lower)}(?![a-zA-Z])'
            if re.search(pattern, text_lower):
                found_skills.append(skill)
        else:
            if skill_lower in text_lower:
                found_skills.append(skill)
    
    # Loại bỏ trùng lặp nhưng giữ thứ tự
    seen = set()
    unique_skills = []
    for s in found_skills:
        s_lower = s.lower()
        if s_lower not in seen:
            seen.add(s_lower)
            unique_skills.append(s)
    
    return ', '.join(unique_skills)


def extract_cv_from_pdf(pdf_path: str) -> dict:
    """
    Pipeline chính: Đọc text PDF → Trích xuất 5 trường CV.
    """
    full_text = extract_text_from_pdf(pdf_path)
    
    if not full_text.strip():
        print("⚠️ [PDF] File PDF không chứa text (có thể là PDF scan/ảnh)")
        return {}
    
    print(f"📄 [PDF] Đã trích xuất {len(full_text)} ký tự text từ PDF")
    print(f"📄 [PDF PREVIEW] {full_text[:300]}...")
    
    raw_data = {
        'level': _find_level(full_text),
        'position': _find_position(full_text),
        'address': _find_address(full_text),
        'gpa': _find_gpa(full_text),
        'skill': _find_skills(full_text),
    }
    
    return raw_data


# --- Test ---
if __name__ == "__main__":
    import json
    import sys
    
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        pdf_file = r"D:\Project\DetectCVLasted\test.pdf"
    
    print(f"📄 Đang xử lý PDF: {pdf_file}")
    
    raw_text = extract_text_from_pdf(pdf_file)
    print(f"\n--- TEXT THÔ TỪ PDF ({len(raw_text)} ký tự) ---")
    print(raw_text[:800])
    print("...\n")
    
    raw_data = extract_cv_from_pdf(pdf_file)
    print("\n--- DỮ LIỆU TRÍCH XUẤT ---")
    print(json.dumps(raw_data, ensure_ascii=False, indent=4))
    
    from text_processor import clean_cv_data
    cleaned = clean_cv_data(raw_data)
    print("\n--- DỮ LIỆU ĐÃ CLEAN ---")
    print(json.dumps(cleaned, ensure_ascii=False, indent=4))
