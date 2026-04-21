import cv2
import os

def crop_and_save_regions(image_path, detected_data, base_output_dir=r"D:\Project\DetectCVLasted\data\cropped_images"):
    """
    Nhận tọa độ từ YOLO, tạo thư mục riêng cho từng ảnh gốc, 
    và dùng OpenCV cắt thành các ảnh nhỏ lưu vào đó.
    """
    # 1. Lấy tên file ảnh gốc (bỏ đuôi .png/.jpg) để làm tên thư mục con
    # Ví dụ: "D:\...\2d187349-IT_56.png" -> "2d187349-IT_56"
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # 2. Tạo đường dẫn thư mục riêng và tạo thư mục đó trên ổ cứng
    specific_output_dir = os.path.join(base_output_dir, image_name)
    os.makedirs(specific_output_dir, exist_ok=True)
    
    # 3. Đọc ảnh gốc bằng OpenCV
    img = cv2.imread(image_path)
    if img is None:
        print(f"Lỗi: Không thể đọc ảnh tại {image_path}")
        return []

    saved_paths = []
    
    # 4. Duyệt qua từng vùng đã detect để cắt
    for region in detected_data:
        label = region['label']
        x1, y1, x2, y2 = region['box']
        
        # Cắt ảnh theo tọa độ (trục y trước, trục x sau)
        cropped_img = img[y1:y2, x1:x2]
        
        # Tạo tên file cho ảnh cắt (ví dụ: gpa.jpg, skill.jpg)
        filename = f"{label}.jpg"
        save_path = os.path.join(specific_output_dir, filename)
        
        # Lưu ảnh con xuống ổ cứng
        cv2.imwrite(save_path, cropped_img)
        saved_paths.append(save_path)
        
        print(f"Đã lưu: {save_path}")
        
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