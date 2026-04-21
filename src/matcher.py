# Code so khớp kết quả JSON với tiêu chí JD của nhà tuyển dụng
import json

def calculate_cv_score(cv_data, jd_criteria):
    """
    So khớp dữ liệu CV với Job Description (JD) và chấm điểm theo trọng số 100.
    """
    scores = {
        "position": 0,
        "gpa": 0,
        "address": 0,
        "level": 0,
        "skill": 0,
        "total": 0
    }
    
    # 1. Chấm điểm Position (Max 10đ)
    # Kiểm tra xem chức danh yêu cầu có nằm trong chức danh của ứng viên không
    jd_pos = jd_criteria.get('position', '').lower()
    cv_pos = cv_data.get('position', '').lower()
    if jd_pos and jd_pos in cv_pos:
        scores["position"] = 10
        
    # 2. Chấm điểm Level (Max 20đ)
    jd_level = jd_criteria.get('level', '').lower()
    cv_level = cv_data.get('level', '').lower()
    if jd_level == cv_level:
        scores["level"] = 20

    # 3. Chấm điểm Address (Max 15đ)
    jd_address = jd_criteria.get('address', '').lower()
    cv_address = cv_data.get('address', '').lower()
    if jd_address and jd_address in cv_address:
        scores["address"] = 15

    # 4. Chấm điểm GPA (Max 25đ) - Chấm tương đối
    try:
        cv_gpa = float(cv_data.get('gpa', 0))
        jd_gpa = float(jd_criteria.get('gpa', 0))
        
        if jd_gpa > 0:
            if cv_gpa >= jd_gpa:
                scores["gpa"] = 25 # Đạt hoặc vượt yêu cầu -> Điểm tối đa
            else:
                # Tính điểm theo tỷ lệ. VD: Yêu cầu 4.0, CV 3.8 -> (3.8 / 4.0) * 25 = 23.75 điểm
                scores["gpa"] = round((cv_gpa / jd_gpa) * 25, 2)
    except ValueError:
        pass # Nếu không parse được ra số thì điểm GPA = 0

    # 5. Chấm điểm Skill (Max 30đ) - Chấm theo số lượng match
    jd_skills = [s.lower() for s in jd_criteria.get('skills', [])]
    cv_skill_text = cv_data.get('skill', '').lower()
    
    if jd_skills:
        matched_count = 0
        matched_skills_list = []
        
        for req_skill in jd_skills:
            if req_skill in cv_skill_text:
                matched_count += 1
                matched_skills_list.append(req_skill)
                
        # Tính điểm tỷ lệ. VD: Yêu cầu 3 skill, match 2 -> (2/3) * 30 = 20 điểm
        skill_score = (matched_count / len(jd_skills)) * 30
        scores["skill"] = round(skill_score, 2)
        scores["matched_skills_detail"] = matched_skills_list # Lưu lại để in ra báo cáo

    # Tổng kết
    scores["total"] = sum([scores["position"], scores["level"], scores["address"], scores["gpa"], scores["skill"]])
    
    return scores

# --- Test thử với dữ liệu thực tế ---
if __name__ == "__main__":
    # 1. Dữ liệu CV đã được làm sạch từ bước trước (text_processor.py)
    cv_cleaned_data = {
        "gpa": "3.9",
        "level": "Junior",
        "position": "Frontend Web Developer",
        "address": "Qun 9 , H Chí Minh",
        "skill": "Python C++ (OpenCV) CUDA (nâng cao) C# (Unity) Version Control DevOps Cơ Bn ework & Runtime"
    }
    
    # 2. Tiêu chí của nhà tuyển dụng (Job Description - JD) giả lập
    jd_requirements = {
        "position": "Frontend",       # Chỉ cần có chữ Frontend
        "level": "Junior",            
        "address": "chí minh",        # Chấp nhận cả "H Chí Minh" hay "Hồ Chí Minh"
        "gpa": 4.0,                   # Yêu cầu khá cao (để test logic chấm tương đối)
        "skills": ["python", "c++", "react"] # Yêu cầu 3 kỹ năng
    }
    
    print("--- TIÊU CHÍ NHÀ TUYỂN DỤNG (JD) ---")
    print(json.dumps(jd_requirements, ensure_ascii=False, indent=4))
    
    # 3. Chạy hàm tính điểm
    result_scores = calculate_cv_score(cv_cleaned_data, jd_requirements)
    
    print("\n--- KẾT QUẢ CHẤM ĐIỂM ỨNG VIÊN ---")
    print(f"1. Position (Max 10): {result_scores['position']}đ")
    print(f"2. Level    (Max 20): {result_scores['level']}đ")
    print(f"3. Address  (Max 15): {result_scores['address']}đ")
    print(f"4. GPA      (Max 25): {result_scores['gpa']}đ (CV: {cv_cleaned_data['gpa']} / Yêu cầu: {jd_requirements['gpa']})")
    
    matched = result_scores.get('matched_skills_detail', [])
    print(f"5. Skill    (Max 30): {result_scores['skill']}đ (Khớp {len(matched)}/{len(jd_requirements['skills'])}: {', '.join(matched)})")
    print("-" * 35)
    print(f"TỔNG ĐIỂM HỒ SƠ: {result_scores['total']} / 100 điểm")
    
    if result_scores['total'] >= 70:
        print("=> ĐÁNH GIÁ: HỒ SƠ ĐẠT YÊU CẦU, CHUYỂN QUA PHỎNG VẤN!")
    else:
        print("=> ĐÁNH GIÁ: HỒ SƠ LOẠI.")