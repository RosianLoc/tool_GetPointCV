import cv2
import os
import numpy as np

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
    
    # 5. Thêm viền trắng (padding) 10px để OCR không bị lẹm viền
    final_img = cv2.copyMakeBorder(final_img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    
    return final_img


def crop_and_save_regions(image_path, detected_data,
                          base_output_dir=r"D:\Project\DetectCVLasted\data\cropped_images"):
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    specific_output_dir = os.path.join(base_output_dir, image_name)
    os.makedirs(specific_output_dir, exist_ok=True)

    img = cv2.imread(image_path)
    if img is None:
        print(f"Lỗi: Không thể đọc ảnh tại {image_path}")
        return []

    img_h, img_w = img.shape[:2]
    saved_paths = []

    for region in detected_data:
        label = region['label']
        x1, y1, x2, y2 = region['box']

        # Thêm padding 8px quanh vùng crop để tránh cắt mất chữ ở rìm
        pad = 8
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(img_w, x2 + pad)
        y2 = min(img_h, y2 + pad)

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