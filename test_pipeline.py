import json
import sys

# Đảm bảo in được UTF-8 trên Windows Terminal
sys.stdout.reconfigure(encoding='utf-8')

from main import process_cv_pipeline

import os
_script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(_script_dir, "data", "raw_cvs", "28627441-IT_322.png")
jd = {
    "position": "Data Engineer",
    "level": "Senior",
    "address": "Hồ Chí Minh",
    "gpa": 3.0,
    "skills": ["python", "sql"]
}

print(f"Đang xử lý pipeline toàn diện cho CV: {image_path}\n")

result = process_cv_pipeline(image_path, jd)

if result:
    print("\n\n✅ KẾT QUẢ CUỐI CÙNG SAU KHI PIPELINE XONG:")
    print("--- DỮ LIỆU ĐỌC ĐƯỢC ---")
    print(json.dumps(result["extracted_data"], ensure_ascii=False, indent=2))
    print("\n--- CHI TIẾT CHẤM ĐIỂM (MATCHER) ---")
    print(json.dumps(result["score_details"], ensure_ascii=False, indent=2))
else:
    print("❌ Lỗi: Không thể nhận diện hoặc xử lý ảnh!")
