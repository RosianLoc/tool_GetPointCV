import json
import re
import unicodedata
from thefuzz import fuzz

# 1. Bổ sung hàm xóa dấu tiếng Việt (Giống NestJS)
def normalize_text(text):
    if not text:
        return ""
    text = str(text).lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    return text

# 2. Xử lý GPA an toàn (Thay phẩy bằng chấm)
def parse_gpa(value):
    if not value: return 0.0
    try:
        cleaned = str(value).replace(',', '.').strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0

def clean_address(text):
    text = normalize_text(text) # Dùng text đã xóa dấu
    keywords = ["thanh pho", "tp", "tinh", "quan", "huyen", "phuong", "xa", "thi xa"]
    for kw in keywords:
        text = text.replace(kw, "")
    return text.strip()

def calculate_cv_score(cv_data, jd_criteria):
    THRESHOLDS = {"position": 80, "level": 85, "address": 60, "skill": 80}
    details = {}
    total = 0

    # 1. Position (Max 10đ)
    jd_pos = normalize_text(jd_criteria.get('position', ''))
    # Lấy thêm fallback từ career_goal nếu position rỗng
    cv_pos_raw = cv_data.get('position', '') or cv_data.get('career_goal', '')
    cv_pos = normalize_text(cv_pos_raw)
    
    if not jd_pos:
        details["position"] = {"jd_value": "", "cv_value": cv_pos, "score": 0, "note": "JD khong yeu cau, bo qua"}
    else:
        ratio = fuzz.partial_ratio(jd_pos, cv_pos)
        score = 10 if ratio >= THRESHOLDS["position"] else 0
        details["position"] = {"jd_value": jd_pos, "cv_value": cv_pos, "fuzzy": ratio, "score": score}
        total += score

    # 2. Level (Max 20đ)
    jd_level = normalize_text(jd_criteria.get('level', ''))
    cv_level = normalize_text(cv_data.get('level', ''))
    
    if not jd_level:
        details["level"] = {"jd_value": "", "cv_value": cv_level, "score": 0, "note": "JD khong yeu cau, bo qua"}
    else:
        ratio = fuzz.ratio(jd_level, cv_level)
        score = 20 if ratio >= THRESHOLDS["level"] else 0
        details["level"] = {"jd_value": jd_level, "cv_value": cv_level, "fuzzy": ratio, "score": score}
        total += score

    # 3. Address (Max 15đ)
    jd_addr_raw = jd_criteria.get('address', '')
    cv_addr_raw = cv_data.get('address', '')
    
    if not jd_addr_raw:
        details["address"] = {"jd_value": "", "cv_value": cv_addr_raw, "score": 0, "note": "JD khong yeu cau, bo qua"}
    else:
        jd_addr = clean_address(jd_addr_raw)
        cv_addr = clean_address(cv_addr_raw)
        ratio = fuzz.partial_ratio(jd_addr, cv_addr)
        score = 15 if ratio >= THRESHOLDS["address"] else 0
        details["address"] = {"jd_value": jd_addr, "cv_value": cv_addr, "fuzzy": ratio, "score": score}
        total += score

    # 4. GPA (Max 25đ) - Sử dụng parse_gpa mới
    cv_gpa = parse_gpa(cv_data.get('gpa'))
    jd_gpa = parse_gpa(jd_criteria.get('gpa'))

    if jd_gpa <= 0:
        details["gpa"] = {"jd_value": jd_gpa, "cv_value": cv_gpa, "score": 0, "note": "JD khong yeu cau, bo qua"}
    else:
        score = 25 if cv_gpa >= jd_gpa else round((cv_gpa / jd_gpa) * 25, 2)
        details["gpa"] = {"jd_value": jd_gpa, "cv_value": cv_gpa, "score": score}
        total += score

    # 5. Skill (Max 30đ)
    raw_jd_skills = jd_criteria.get('skills', [])
    cv_skill_raw = cv_data.get('skill', '') or cv_data.get('skills', '')
    
    # Xử lý list skill thành chuỗi, sau đó xóa dấu
    if isinstance(cv_skill_raw, list):
        cv_skill_text = normalize_text(', '.join(cv_skill_raw))
    else:
        cv_skill_text = normalize_text(cv_skill_raw)

    if isinstance(raw_jd_skills, str):
        jd_skills_raw = [s.strip() for s in re.split(r'[,;\n|]', raw_jd_skills) if s.strip()]
    else:
        jd_skills_raw = raw_jd_skills if raw_jd_skills else []
        
    jd_skills = [normalize_text(s) for s in jd_skills_raw if len(s) > 1]

    if not jd_skills:
        details["skill"] = {"jd_value": [], "cv_value": cv_skill_text, "score": 0, "note": "JD khong yeu cau, bo qua"}
    else:
        matched = [s for s in jd_skills if fuzz.partial_ratio(s, cv_skill_text) >= THRESHOLDS["skill"]]
        score = round((len(matched) / len(jd_skills)) * 30, 2)
        details["skill"] = {
            "jd_value": jd_skills,
            "cv_value": cv_skill_text,
            "matched": matched,
            "unmatched": [s for s in jd_skills if s not in matched],
            "score": score
        }
        total += score

    details["total"] = round(total, 2)
    return details