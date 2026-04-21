import re
import json

def clean_cv_data(raw_data):
    cleaned_data = {}
    
    # --- 1. GOM DỮ LIỆU BỊ LOẠN VÀO 1 RỔ ---
    # Lấy giá trị của 3 trường hay bị YOLO gán nhãn lung tung nhất
    pool_of_texts = [
        raw_data.get('level', '').strip(),
        raw_data.get('position', '').strip(),
        raw_data.get('address', '').strip()
    ]
    
    # Lọc bỏ các chuỗi rỗng (nếu OCR không đọc được gì)
    pool_of_texts = [text for text in pool_of_texts if text]

    final_level = ""
    final_address = ""
    final_position = ""

    # --- 2. LUẬT PHÂN LOẠI (CONTENT-BASED ROUTING) ---
    known_levels = ['intern', 'fresher', 'junior', 'middle', 'mid', 'senior', 'lead', 'manager']
    # Thêm các từ khóa nhận diện địa chỉ (chú ý bắt cả các lỗi sai chính tả từ OCR như "qun", "h chi minh")
    address_keywords = ['quận', 'qun', 'q.', 'phố', 'h chí minh', 'h chi minh', 'hồ chí minh', 'hà nội', 'hn', 'hcm', 'phường', 'đường', 'tỉnh']

    # BƯỚC 2.1: Tìm Level trong rổ
    for text in pool_of_texts[:]: # Lặp qua bản sao của list
        text_lower = text.lower()
        if any(lvl in text_lower.split() for lvl in known_levels):
            final_level = text
            pool_of_texts.remove(text) # Nhặt ra rồi thì xóa khỏi rổ
            break # Tìm thấy rồi thì dừng

    # BƯỚC 2.2: Tìm Address trong rổ
    for text in pool_of_texts[:]:
        text_lower = text.lower()
        if any(kw in text_lower for kw in address_keywords):
            final_address = text
            pool_of_texts.remove(text)
            break

    # BƯỚC 2.3: Cái còn sót lại cuối cùng chính là Position
    if pool_of_texts:
        final_position = " ".join(pool_of_texts)

    # Gán lại dữ liệu đã dọn dẹp chuẩn xác
    cleaned_data['level'] = final_level
    cleaned_data['position'] = final_position
    cleaned_data['address'] = final_address

    # --- 3. XỬ LÝ GPA VÀ SKILL (Giữ nguyên vì ít bị lộn) ---
    raw_gpa = raw_data.get('gpa', '')
    gpa_match = re.search(r'(\d+\.\d+)', raw_gpa)
    cleaned_data['gpa'] = gpa_match.group(1) if gpa_match else "0"

    raw_skill = raw_data.get('skill', '')
    cleaned_data['skill'] = " ".join(raw_skill.split())
    
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