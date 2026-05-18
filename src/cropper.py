import cv2
import os
import numpy as np

def preprocess_for_ocr(img):
    """
    Tăng chất lượng ảnh crop trước khi đưa vào OCR:
    1. Upscale 2x → chữ to hơn, OCR đọc chính xác hơn
    2. Sharpen → làm nét cạnh chữ
    3. Denoise → giảm nhiễu ảnh
    """
    # 1. Upscale 2x bằng INTER_CUBIC (giữ nét hơn INTER_LINEAR)
    h, w = img.shape[:2]
    img = cv2.resize(img, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

    # 2. Sharpen
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)

    # 3. Denoise nhẹ để không mất nét chữ
    img = cv2.fastNlMeansDenoisingColored(img, None, h=7, hColor=7,
                                          templateWindowSize=7, searchWindowSize=21)
    return img


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