import cv2
import os
import numpy as np
from ultralytics import YOLO

# ================= CẤU HÌNH ĐƯỜNG DẪN =================
MODEL_PATH = r"D:\Project\DetectCVLasted\runs7\weights\best.pt"           # Đường dẫn model YOLO xịn nhất
TEST_DIR = r"data\raw_cvs"                      # Thư mục chứa 30 ảnh CV test
OUTPUT_CROP_DIR = r"data\cropped_images"        # Thư mục lưu ảnh đã cắt
# ======================================================

def preprocess_for_ocr(img):
    """ Tăng chất lượng ảnh crop trước khi đưa vào OCR """
    # 1. Chuyển sang ảnh xám (Grayscale)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Upscale 2x để phóng to các chữ nhỏ
    h, w = gray.shape[:2]
    gray = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

    # 3. Tăng độ tương phản cực đại bằng CLAHE (Tốt hơn Denoise mờ)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)

    # 4. Sharpen (Làm sắc nét viền chữ)
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    final_img = cv2.filter2D(enhanced, -1, kernel)
    
    # Optional: Thêm viền trắng (padding) 10px để OCR không bị lẹm viền
    final_img = cv2.copyMakeBorder(final_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    
    return final_img

def get_cv_boxes(image_path, model):
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

def crop_and_save_regions(image_path, detected_data, base_output_dir):
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    specific_output_dir = os.path.join(base_output_dir, image_name)
    os.makedirs(specific_output_dir, exist_ok=True)

    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Lỗi: Không thể đọc ảnh tại {image_path}")
        return []

    img_h, img_w = img.shape[:2]
    saved_paths = []

    for region in detected_data:
        label = region['label']
        x1, y1, x2, y2 = region['box']

        # Thêm padding 8px quanh vùng crop
        pad = 8
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(img_w, x2 + pad)
        y2 = min(img_h, y2 + pad)

        cropped = img[y1:y2, x1:x2]
        if cropped.size == 0:
            continue

        cropped = preprocess_for_ocr(cropped)
        save_path = os.path.join(specific_output_dir, f"{label}.png")
        cv2.imwrite(save_path, cropped)
        saved_paths.append(save_path)

    return saved_paths

if __name__ == "__main__":
    print("🚀 Đang khởi tạo mô hình YOLO...")
    model = YOLO(MODEL_PATH)
    
    image_files = [f for f in os.listdir(TEST_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"📦 Tìm thấy {len(image_files)} ảnh trong tập Test.\n")
    
    for img_file in image_files:
        img_path = os.path.join(TEST_DIR, img_file)
        print(f"--- Đang xử lý: {img_file} ---")
        
        cv_regions = get_cv_boxes(img_path, model)
        print(f"🎯 Tìm thấy {len(cv_regions)} vùng dữ liệu.")
        
        saved = crop_and_save_regions(img_path, cv_regions, OUTPUT_CROP_DIR)
        print(f"✂️ Đã cắt và lưu {len(saved)} ảnh con.\n")

    print("✅ HOÀN TẤT BƯỚC 1!")
    print(f"👉 Ảnh YOLO vẽ khung xem tại: thư mục 'runs/detect/predict...'")
    print(f"👉 Ảnh đã cắt nét căng xem tại: {OUTPUT_CROP_DIR}")