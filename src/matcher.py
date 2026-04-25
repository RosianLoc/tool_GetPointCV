import json
import re
from thefuzz import fuzz

# Hàm làm sạch địa chỉ để tăng độ chính xác
def clean_address(text):
    text = text.lower()
    keywords = ["thành phố", "tp", "tỉnh", "quận", "huyện", "phường", "xã", "thị xã"]
    for kw in keywords:
        text = text.replace(kw, "")
    return text.strip()

def calculate_cv_score(cv_data, jd_criteria):
    scores = {
        "position": 0, "gpa": 0, "address": 0, "level": 0, "skill": 0, "total": 0
    }
    
    # [CẢI TIẾN]: BỘ CẤU HÌNH NGƯỠNG ĐIỂM (THRESHOLDS) RIÊNG BIỆT
    THRESHOLDS = {
        "position": 80,
        "level": 85,    # Tăng lên 85 vì level thường là từ ngắn, cần chính xác
        "address": 60,  # 60 là hoàn hảo để chấp nhận lỗi OCR và viết tắt
        "skill": 80
    }
    
    # 1. Chấm điểm Position (Max 10đ)
    jd_pos = jd_criteria.get('position', '').lower()
    cv_pos = cv_data.get('position', '').lower()
    if jd_pos and fuzz.partial_ratio(jd_pos, cv_pos) >= THRESHOLDS["position"]:
        scores["position"] = 10
        
    # 2. Chấm điểm Level (Max 20đ)
    jd_level = jd_criteria.get('level', '').lower()
    cv_level = cv_data.get('level', '').lower()
    # Level nên dùng ratio (so sánh toàn bộ chữ) thay vì partial
    if fuzz.ratio(jd_level, cv_level) >= THRESHOLDS["level"]:
        scores["level"] = 20

    # 3. Chấm điểm Address (Max 15đ) - Đã kết hợp làm sạch rác
    jd_address = clean_address(jd_criteria.get('address', ''))
    cv_address = clean_address(cv_data.get('address', ''))
    if jd_address and fuzz.partial_ratio(jd_address, cv_address) >= THRESHOLDS["address"]:
        scores["address"] = 15

    # 4. Chấm điểm GPA (Toán học, không dùng Fuzzy Threshold)
    try:
        cv_gpa = float(cv_data.get('gpa', 0))
        jd_gpa = float(jd_criteria.get('gpa', 0))
        if jd_gpa > 0:
            if cv_gpa >= jd_gpa:
                scores["gpa"] = 25 
            else:
                scores["gpa"] = round((cv_gpa / jd_gpa) * 25, 2)
        else:
            scores["gpa"] = 25 # Nếu không yêu cầu GPA thì auto max điểm
    except ValueError:
        pass 

    # 5. Chấm điểm Skill (Max 30đ)
    raw_jd_skills = jd_criteria.get('skills', '')
    cv_skill_text = cv_data.get('skill', '').lower()
    
    if isinstance(raw_jd_skills, str):
        jd_skills = [s.strip().lower() for s in re.split(r'[,;\n|]', raw_jd_skills) if s.strip()]
    else:
        jd_skills = [s.lower() for s in raw_jd_skills] if raw_jd_skills else []
    
    if jd_skills:
        matched_count = 0
        matched_skills_list = []
        
        for req_skill in jd_skills:
            # Lọc bỏ từ khóa ngắn và áp dụng Threshold 80 cho Skill
            if len(req_skill) > 1 and fuzz.partial_ratio(req_skill, cv_skill_text) >= THRESHOLDS["skill"]:
                matched_count += 1
                matched_skills_list.append(req_skill)
                
        skill_score = (matched_count / len(jd_skills)) * 30
        scores["skill"] = round(skill_score, 2)
        scores["matched_skills_detail"] = matched_skills_list 
    else:
        scores["skill"] = 30
        scores["matched_skills_detail"] = []

    # TỔNG KẾT
    scores["total"] = sum([scores["position"], scores["level"], scores["address"], scores["gpa"], scores["skill"]])
    return scores