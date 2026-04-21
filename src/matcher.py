import json
from thefuzz import fuzz # Import thư viện Fuzzy Matching

def calculate_cv_score(cv_data, jd_criteria):
    scores = {
        "position": 0, "gpa": 0, "address": 0, "level": 0, "skill": 0, "total": 0
    }
    
    # Định mức điểm chuẩn (ngưỡng giống nhau) để chấp nhận là Match
    THRESHOLD = 80 
    
    # 1. Chấm điểm Position (Max 10đ)
    jd_pos = jd_criteria.get('position', '').lower()
    cv_pos = cv_data.get('position', '').lower()
    # Dùng partial_ratio: Kiểm tra xem jd_pos có nằm lọt thỏm và giống cv_pos không
    if jd_pos and fuzz.partial_ratio(jd_pos, cv_pos) >= THRESHOLD:
        scores["position"] = 10
        
    # 2. Chấm điểm Level (Max 20đ)
    jd_level = jd_criteria.get('level', '').lower()
    cv_level = cv_data.get('level', '').lower()
    # Dùng ratio: So sánh độ giống nhau của 2 chuỗi ngắn
    if fuzz.ratio(jd_level, cv_level) >= THRESHOLD:
        scores["level"] = 20

    # 3. Chấm điểm Address (Max 15đ)
    jd_address = jd_criteria.get('address', '').lower()
    cv_address = cv_data.get('address', '').lower()
    if jd_address and fuzz.partial_ratio(jd_address, cv_address) >= THRESHOLD:
        scores["address"] = 15

    # 4. Chấm điểm GPA (Giữ nguyên logic của bạn vì xử lý số)
    try:
        cv_gpa = float(cv_data.get('gpa', 0))
        jd_gpa = float(jd_criteria.get('gpa', 0))
        if jd_gpa > 0:
            if cv_gpa >= jd_gpa:
                scores["gpa"] = 25 
            else:
                scores["gpa"] = round((cv_gpa / jd_gpa) * 25, 2)
    except ValueError:
        pass 

    # 5. Chấm điểm Skill (Max 30đ) - Áp dụng Fuzzy Match
    jd_skills = [s.lower() for s in jd_criteria.get('skills', [])]
    cv_skill_text = cv_data.get('skill', '').lower()
    
    if jd_skills:
        matched_count = 0
        matched_skills_list = []
        
        for req_skill in jd_skills:
            # Nếu kỹ năng yêu cầu (vd: python) giống với một đoạn nào đó trong chuỗi skill của CV từ 80% trở lên
            if fuzz.partial_ratio(req_skill, cv_skill_text) >= THRESHOLD:
                matched_count += 1
                matched_skills_list.append(req_skill)
                
        skill_score = (matched_count / len(jd_skills)) * 30
        scores["skill"] = round(skill_score, 2)
        scores["matched_skills_detail"] = matched_skills_list 

    scores["total"] = sum([scores["position"], scores["level"], scores["address"], scores["gpa"], scores["skill"]])
    return scores