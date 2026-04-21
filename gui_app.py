import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

# Import hàm xử lý chính từ file main.py của bạn
from main import process_cv_pipeline

class CVParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống AI Lọc CV Tự Động")
        self.root.geometry("1000x650")
        
        self.selected_cv_paths = []

        self.setup_ui()

    def setup_ui(self):
        # ================= PHẦN 1: NHẬP TIÊU CHÍ (JD) =================
        jd_frame = tk.LabelFrame(self.root, text="1. Tiêu chí Nhà tuyển dụng (JD)", padx=10, pady=10)
        jd_frame.pack(fill="x", padx=10, pady=5)

        # Các biến lưu trữ dữ liệu nhập vào
        self.var_position = tk.StringVar(value="Frontend")
        self.var_level = tk.StringVar(value="Junior")
        self.var_address = tk.StringVar(value="Hồ Chí Minh")
        self.var_gpa = tk.StringVar(value="3.5")
        self.var_skills = tk.StringVar(value="python, c++, react")

        # Layout form nhập liệu
        tk.Label(jd_frame, text="Vị trí (Position):").grid(row=0, column=0, sticky="w", pady=5)
        tk.Entry(jd_frame, textvariable=self.var_position, width=25).grid(row=0, column=1, padx=5)

        tk.Label(jd_frame, text="Cấp bậc (Level):").grid(row=0, column=2, sticky="w", padx=(20, 0))
        tk.Entry(jd_frame, textvariable=self.var_level, width=25).grid(row=0, column=3, padx=5)

        tk.Label(jd_frame, text="Địa điểm (Address):").grid(row=1, column=0, sticky="w", pady=5)
        tk.Entry(jd_frame, textvariable=self.var_address, width=25).grid(row=1, column=1, padx=5)

        tk.Label(jd_frame, text="GPA Tối thiểu:").grid(row=1, column=2, sticky="w", padx=(20, 0))
        tk.Entry(jd_frame, textvariable=self.var_gpa, width=25).grid(row=1, column=3, padx=5)

        tk.Label(jd_frame, text="Kỹ năng (Cách nhau bằng dấu phẩy):").grid(row=2, column=0, sticky="w", pady=5)
        tk.Entry(jd_frame, textvariable=self.var_skills, width=65).grid(row=2, column=1, columnspan=3, sticky="w", padx=5)

        # ================= PHẦN 2: TẢI LÊN CV & NÚT XỬ LÝ =================
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=10)

        self.btn_upload = tk.Button(action_frame, text="📁 Chọn các file CV (Ảnh)", command=self.upload_cvs, bg="#f0f0f0", height=2)
        self.btn_upload.pack(side="left", padx=(0, 10))

        self.lbl_cv_count = tk.Label(action_frame, text="Chưa chọn CV nào.", fg="blue")
        self.lbl_cv_count.pack(side="left", padx=10)

        self.btn_start = tk.Button(action_frame, text="🚀 BẮT ĐẦU LỌC CV", command=self.start_processing, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), height=2)
        self.btn_start.pack(side="right")

        # ================= PHẦN 3: BẢNG KẾT QUẢ =================
        result_frame = tk.LabelFrame(self.root, text="2. Kết quả Đánh giá", padx=10, pady=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Khởi tạo bảng (Treeview)
        columns = ("file", "total", "position", "level", "address", "gpa", "skill", "status")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=15)
        
        # Định nghĩa các cột
        self.tree.heading("file", text="Tên file CV")
        self.tree.heading("total", text="Tổng điểm")
        self.tree.heading("position", text="Position (10)")
        self.tree.heading("level", text="Level (20)")
        self.tree.heading("address", text="Address (15)")
        self.tree.heading("gpa", text="GPA (25)")
        self.tree.heading("skill", text="Skill (30)")
        self.tree.heading("status", text="Đánh giá")

        # Căn chỉnh độ rộng cột
        self.tree.column("file", width=150)
        self.tree.column("total", width=80, anchor="center")
        self.tree.column("position", width=80, anchor="center")
        self.tree.column("level", width=80, anchor="center")
        self.tree.column("address", width=80, anchor="center")
        self.tree.column("gpa", width=80, anchor="center")
        self.tree.column("skill", width=80, anchor="center")
        self.tree.column("status", width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, side="left")
        
        # Thêm thanh cuộn (Scrollbar) cho bảng
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def upload_cvs(self):
        # Mở hộp thoại chọn nhiều file
        files = filedialog.askopenfilenames(
            title="Chọn ảnh CV",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if files:
            self.selected_cv_paths = list(files)
            self.lbl_cv_count.config(text=f"Đã chọn {len(self.selected_cv_paths)} CV. Sẵn sàng lọc!")

    def start_processing(self):
        if not self.selected_cv_paths:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 1 CV để lọc!")
            return

        # Xóa dữ liệu cũ trong bảng
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Lấy tiêu chí JD từ UI
        jd_requirements = {
            "position": self.var_position.get().strip(),
            "level": self.var_level.get().strip(),
            "address": self.var_address.get().strip(),
            "gpa": float(self.var_gpa.get()) if self.var_gpa.get().replace('.','',1).isdigit() else 0.0,
            "skills": [s.strip() for s in self.var_skills.get().split(",") if s.strip()]
        }

        # Khóa nút bấm để tránh click nhiều lần
        self.btn_start.config(state="disabled", text="Đang xử lý...")
        
        # Chạy AI ở một luồng (thread) riêng để giao diện không bị đơ
        threading.Thread(target=self.run_pipeline_thread, args=(jd_requirements,), daemon=True).start()

    def run_pipeline_thread(self, jd_requirements):
        for idx, cv_path in enumerate(self.selected_cv_paths):
            filename = os.path.basename(cv_path)
            
            try:
                # Gọi hàm AI cốt lõi từ main.py
                score_result = process_cv_pipeline(cv_path, jd_requirements)
                
                if score_result:
                    # Đánh giá Đạt / Loại
                    status = "✅ ĐẠT" if score_result['total'] >= 70 else "❌ LOẠI"
                    
                    # Chèn kết quả vào bảng
                    self.tree.insert("", tk.END, values=(
                        filename,
                        f"{score_result['total']} / 100",
                        score_result['position'],
                        score_result['level'],
                        score_result['address'],
                        score_result['gpa'],
                        score_result['skill'],
                        status
                    ))
                else:
                    self.tree.insert("", tk.END, values=(filename, "Lỗi đọc AI", "-", "-", "-", "-", "-", "⚠️ LỖI"))
                    
            except Exception as e:
                print(f"Lỗi khi xử lý {filename}: {e}")
                self.tree.insert("", tk.END, values=(filename, "Lỗi Hệ Thống", "-", "-", "-", "-", "-", "⚠️ LỖI"))

        # Mở khóa nút bấm khi chạy xong
        self.btn_start.config(state="normal", text="🚀 BẮT ĐẦU LỌC CV")
        messagebox.showinfo("Hoàn tất", "Đã quét và lọc xong toàn bộ CV!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CVParserApp(root)
    root.mainloop()