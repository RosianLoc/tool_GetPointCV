import cv2
import os
import numpy as np
from ultralytics import YOLO

# ================= CẤU HÌNH ĐƯỜNG DẪN =================
MODEL_PATH = r"D:\Project\DetectCVLasted\runs8\weights\best.pt"           # Đường dẫn model YOLO xịn nhất
TEST_DIR = r"data\raw_cvs"                      # Thư mục chứa 30 ảnh CV test
OUTPUT_CROP_DIR = r"data\cropped_images"        # Thư mục lưu ảnh đã cắt
# ======================================================

from src.cropper import crop_and_save_regions

def get_cv_boxes_local(image_path, model):
    """ Load model YOLO và trả về danh sách tọa độ, nhãn """
    results = model(
        image_path, conf=0.55, imgsz=1280, iou=0.5,
        verbose=False, save=True # Bật save=True để YOLO tự lưu ảnh vẽ khung vào runs/detect/predict
    )
    
    detected_data = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            label = r.names[class_id]
            conf = float(box.conf[0])
            detected_data.append({
                "label": label, "box": [x1, y1, x2, y2], "confidence": conf
            })
    return detected_data

if __name__ == "__main__":
    print("🚀 Đang khởi tạo mô hình YOLO...")
    model = YOLO(MODEL_PATH)
    
    image_files = [f for f in os.listdir(TEST_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"📦 Tìm thấy {len(image_files)} ảnh trong tập Test.\n")
    
    for img_file in image_files:
        img_path = os.path.join(TEST_DIR, img_file)
        print(f"--- Đang xử lý: {img_file} ---")
        
        cv_regions = get_cv_boxes_local(img_path, model)
        print(f"🎯 Tìm thấy {len(cv_regions)} vùng dữ liệu.")
        
        saved = crop_and_save_regions(img_path, cv_regions, OUTPUT_CROP_DIR)
        print(f"✂️ Đã cắt và lưu {len(saved)} ảnh con.\n")

    print("✅ HOÀN TẤT BƯỚC 1!")
    print(f"👉 Ảnh YOLO vẽ khung xem tại: thư mục 'runs/detect/predict...'")
    print(f"👉 Ảnh đã cắt nét căng xem tại: {OUTPUT_CROP_DIR}")