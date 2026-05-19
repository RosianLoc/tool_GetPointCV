import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

from src.matcher import calculate_cv_score

jd = {
    "position": "Developer",
    "level": "Junior",
    "address": "Hồ Chí Minh",
    "gpa": 3.0,
    "skills": ["C", "C++", "C#", "React", "Python"]
}

# Giả lập ứng viên không biết C, C++, C# nhưng có React và HTML, CSS
cv_data_1 = {
    "position": "Frontend Developer",
    "level": "Junior",
    "address": "Thành phố Hồ Chí Minh",
    "gpa": "3.5",
    "skill": "ReactJS, HTML, CSS, JavaScript"
}

# Giả lập ứng viên có đủ các môn
cv_data_2 = {
    "position": "Backend Developer",
    "level": "Junior",
    "address": "Quận 1, Hồ Chí Minh",
    "gpa": "3.2",
    "skill": "C++, C#, Python, SQL"
}

print("=== TEST CASE 1: Ứng viên Frontend (Nên bỏ qua chữ C vì không đúng kỹ năng) ===")
score1 = calculate_cv_score(cv_data_1, jd)
print(json.dumps(score1["skill"], ensure_ascii=False, indent=2))
print("Tổng điểm:", score1["total"])

print("\n=== TEST CASE 2: Ứng viên Backend (Đủ C++, C# và Python) ===")
score2 = calculate_cv_score(cv_data_2, jd)
print(json.dumps(score2["skill"], ensure_ascii=False, indent=2))
print("Tổng điểm:", score2["total"])
