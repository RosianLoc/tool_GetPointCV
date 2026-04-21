import re
import json

def clean_cv_data(raw_data):
    """
    Làm sạch dữ liệu, bóc tách và hoán đổi lại các nhãn bị YOLO nhận diện nhầm.
    """
    cleaned_data = {}
    
    # --- BƯỚC 1: SWITCH (HOÁN ĐỔI) DỮ LIỆU ---
    # Lấy chéo dữ liệu thô để đưa về đúng ngữ nghĩa thực tế
    raw_actual_address = raw_data.get('position', '') # Đang chứa "Qun 9 , H Chí Minh"
    raw_actual_position = raw_data.get('address', '') # Đang chứa "Junior Frontend Web Developer"
    
    # --- BƯỚC 2: XỬ LÝ LÀM SẠCH ---
    
    # 1. Xử lý GPA: Chỉ lấy số đầu tiên
    raw_gpa = raw_data.get('gpa', '')
    gpa_match = re.search(r'(\d+\.\d+)', raw_gpa)
    cleaned_data['gpa'] = gpa_match.group(1) if gpa_match else ""

    # 2. Xử lý Level: Lấy chữ đầu tiên
    raw_level = raw_data.get('level', '').strip()
    cleaned_data['level'] = raw_level.split()[0] if raw_level else ""
        
    # 3. Xử lý Position (Chức danh): Bỏ chữ đầu tiên (vì chữ đầu là Level)
    # VD: "Junior Frontend Web Developer" -> "Frontend Web Developer"
    raw_actual_position = raw_actual_position.strip()
    if raw_actual_position:
        words = raw_actual_position.split()
        # Nối từ phần tử thứ 2 trở đi, nếu chỉ có 1 từ thì lấy luôn từ đó
        cleaned_data['position'] = " ".join(words[1:]) if len(words) > 1 else raw_actual_position
    else:
        cleaned_data['position'] = ""

    # 4. Xử lý Address (Địa chỉ): Giữ nguyên, chỉ dọn dẹp khoảng trắng thừa
    # VD: "Qun 9 , H Chí Minh" -> "Qun 9 , H Chí Minh"
    cleaned_data['address'] = " ".join(raw_actual_address.split())

    # 5. Xử lý Skill: Dọn dẹp khoảng trắng
    raw_skill = raw_data.get('skill', '')
    cleaned_data['skill'] = " ".join(raw_skill.split())
    
    return cleaned_data

# --- Test thử với dữ liệu OCR ---
if __name__ == "__main__":
    # Dữ liệu bị ngược từ OCR
    raw_ocr_output = {
        "address": "Junior Frontend Web Developer",
        "gpa": "GPA:3.9/4.0",
        "level": "Junior Frontend Web Developer",
        "position": "Qun 9 , H Chí Minh",
        "skill": "Python C++ (OpenCV) CUDA (nâng cao) C# (Unity) Version Control DevOps Cơ Bn ework & Runtime"
    }
    
    final_json = clean_cv_data(raw_ocr_output)
    
    print("--- DỮ LIỆU SAU KHI SWITCH VÀ LÀM SẠCH ---")
    print(json.dumps(final_json, ensure_ascii=False, indent=4))