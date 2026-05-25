import os
from ultralytics import YOLO

# Resolve dynamic relative path to runs8/weights/best.pt
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
_default_model = os.path.join(_parent_dir, "runs8", "weights", "best.pt")

def get_cv_boxes(image_path, model_path=_default_model):
    """
    Load model YOLO và trả về danh sách tọa độ, nhãn của các vùng trên CV.
    """
    # 1. Load model
    model = YOLO(model_path)
    
    # 2. Predict
    results = model(
        image_path,
        conf=0.55,
        imgsz=1280,
        iou=0.5,
        verbose=False # Tắt bớt log rác trên terminal
    )
    
    detected_data = []
    
    # 3. Trích xuất dữ liệu từ results
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Lấy tọa độ x_min, y_min, x_max, y_max và ép kiểu về số nguyên (int) để tiện cắt ảnh sau này
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Lấy ID của class và tra cứu tên nhãn
            class_id = int(box.cls[0])
            label = r.names[class_id]
            
            # Lấy độ tự tin (confidence score)
            conf = float(box.conf[0])
            
            # Đóng gói thành Dictionary và đưa vào list
            detected_data.append({
                "label": label,
                "box": [x1, y1, x2, y2],
                "confidence": conf
            })
            
    return detected_data

# --- Phần này chỉ chạy khi bạn test trực tiếp file detector.py ---
if __name__ == "__main__":
    test_image = os.path.join(_parent_dir, "data", "raw_cvs", "2d187349-IT_56.png")
    
    # Gọi hàm và in kết quả ra xem thử
    cv_regions = get_cv_boxes(test_image)
    
    print(f"\nĐã tìm thấy {len(cv_regions)} vùng:")
    for region in cv_regions:
        print(f"- Nhãn: {region['label']:<10} | Tọa độ: {region['box']} | Conf: {region['confidence']:.2f}")