import cv2
import os
import shutil
import numpy as np

def preprocess_for_ocr(img):
    """ Tăng chất lượng ảnh crop trước khi đưa vào OCR """
    # 1. Chuyển sang ảnh xám (Grayscale)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Upscale 2x để phóng to các chữ nhỏ
    h, w = gray.shape[:2]
    gray = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

    # 3. Khử nhiễu (Bilateral Filter) giúp xóa nhiễu nền nhưng vẫn giữ sắc nét chữ
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)

    # 4. Tăng độ tương phản (CLAHE) thay vì Sharpen (Sharpen dễ làm rách chữ)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # 5. Thêm viền trắng (padding) 20px để OCR nhận diện tốt hơn ở các góc
    final_img = cv2.copyMakeBorder(enhanced, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    
    return final_img


def crop_and_save_regions(image_path, detected_data,
                          base_output_dir=r"D:\Project\DetectCVLasted\data\cropped_images"):
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    specific_output_dir = os.path.join(base_output_dir, image_name)
    os.makedirs(specific_output_dir, exist_ok=True)

    # XÓA file cũ trong thư mục trước khi lưu crop mới
    # Tránh file cũ (từ lần chạy trước) bị OCR đọc lại gây trùng lặp
    for old_file in os.listdir(specific_output_dir):
        old_path = os.path.join(specific_output_dir, old_file)
        if os.path.isfile(old_path):
            os.remove(old_path)

    img = cv2.imread(image_path)
    if img is None:
        print(f"Lỗi: Không thể đọc ảnh tại {image_path}")
        return []

    img_h, img_w = img.shape[:2]
    saved_paths = []

    label_counts = {}

    for region in detected_data:
        base_label = region['label']
        label_counts[base_label] = label_counts.get(base_label, 0) + 1
        label = f"{base_label}_{label_counts[base_label]}"
        
        x1, y1, x2, y2 = region['box']

        # Dùng padding âm (thụt vào trong) để cắt thật sát, tránh lẹm viền do YOLO box hơi rộng.
        pad_y = -2  # Thụt vào 2px theo chiều dọc
        pad_x = -1  # Thụt vào 1px theo chiều ngang
        
        x1 = max(0, x1 - pad_x)
        y1 = max(0, y1 - pad_y)
        x2 = min(img_w, x2 + pad_x)
        y2 = min(img_h, y2 + pad_y)

        # Đảm bảo box hợp lệ sau khi thu nhỏ
        if x1 >= x2 or y1 >= y2:
            continue

        cropped = img[y1:y2, x1:x2]
        if cropped.size == 0:
            continue

        # Preprocess trước khi lưu
        cropped = preprocess_for_ocr(cropped)

        # Lưu PNG thay vì JPEG để không bị nén mất chất lượng
        save_path = os.path.join(specific_output_dir, f"{label}.png")
        cv2.imwrite(save_path, cropped)
        saved_paths.append(save_path)

    return saved_paths

# --- Test thử ---
if __name__ == "__main__":
    from detector import get_cv_boxes 
    
    test_image = r"D:\Project\DetectCVLasted\data\raw_cvs\2d187349-IT_56.png"
    
    print(f"1. Đang lấy tọa độ từ YOLO cho ảnh {os.path.basename(test_image)}...")
    cv_regions = get_cv_boxes(test_image)
    
    print("2. Đang tiến hành cắt ảnh...")
    crop_and_save_regions(test_image, cv_regions)
    print("\nHoàn tất! Hãy kiểm tra thư mục cropped_images.")