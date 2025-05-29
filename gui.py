import tkinter as tk
from tkinter import messagebox, Toplevel, Entry, Label, Button
from system import ElevatorSystem

class ElevatorGUI:
    def __init__(self, root, elevator_system):
        self.elevator_system = elevator_system
        self.root = root
        self.root.title("Mô phỏng 2 Thang máy - 20 Tầng")
        self.requests = []
        self.root.state('zoomed')
        self.root.resizable(True, True)
        self.root.configure(bg="lightblue")
        self.main_frame = tk.Frame(root, bg="lightblue")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.elevator1_frame = tk.Frame(self.main_frame, bg="lightblue")
        self.elevator1_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.Y)
        self.control_frame = tk.Frame(self.main_frame, bg="lightyellow", relief=tk.RAISED, borderwidth=2)
        self.control_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.Y)
        self.elevator2_frame = tk.Frame(self.main_frame, bg="lightblue")
        self.elevator2_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.Y)

        self.status1_frame = tk.Frame(self.elevator1_frame, bg="lightblue")
        self.status1_frame.pack(pady=5)
        self.label1_floor = tk.Label(self.status1_frame, text=f"TM1 Tầng: {elevator_system.elevators[0].current_floor}",
                                     font=("Arial", 12), bg="lightblue")
        self.label1_floor.pack()
        self.label1_direction = tk.Label(self.status1_frame,
                                         text=f"TM1 Hướng: {elevator_system.elevators[0].direction}",
                                         font=("Arial", 12), bg="lightblue")
        self.label1_direction.pack()
        self.label1_door = tk.Label(self.status1_frame,
                                    text=f"TM1 Cửa: {'Mở' if elevator_system.elevators[0].door_open else 'Đóng'}",
                                    font=("Arial", 12), bg="lightblue")
        self.label1_door.pack()

        self.canvas1 = tk.Canvas(self.elevator1_frame, width=200, height=550, bg="lightgrey")
        self.canvas1.pack(pady=10)
        self.draw_building(self.canvas1, elevator_system.elevators[0])

        self.select1_frame = tk.Frame(self.elevator1_frame, bg="lightblue")
        self.select1_frame.pack(pady=5)
        tk.Label(self.select1_frame, text="TM1 Chọn tầng", font=("Arial", 12), bg="lightblue").pack()
        row1 = tk.Frame(self.select1_frame, bg="lightblue")
        row1.pack()
        row2 = tk.Frame(self.select1_frame, bg="lightblue")
        row2.pack()
        for i in range(20, 10, -1):
            button_color = "yellow" if i in [18, 19, 20] else "white"
            tk.Button(row1, text=f"T{i}", command=lambda x=i: self.request_floor(elevator_system.elevators[0], x),
                      width=4, bg=button_color).pack(side=tk.LEFT, padx=2)
        for i in range(10, 0, -1):
            tk.Button(row2, text=f"T{i}", command=lambda x=i: self.request_floor(elevator_system.elevators[0], x),
                      width=4).pack(side=tk.LEFT, padx=2)

        self.call_frame = tk.Frame(self.control_frame, bg="lightyellow")
        self.call_frame.pack(pady=5)
        tk.Label(self.call_frame, text="Gọi thang ngoài", font=("Arial", 12), bg="lightyellow").pack()
        for i in range(elevator_system.elevators[0].num_floors, 0, -1):
            floor_frame = tk.Frame(self.call_frame, bg="lightyellow")
            floor_frame.pack(pady=2)
            tk.Label(floor_frame, text=f"Tầng {i}", width=8, font=("Arial", 10), bg="lightyellow").pack(side=tk.LEFT)
            if i == elevator_system.elevators[0].num_floors:
                tk.Button(floor_frame, text="Xuống", command=lambda x=i: self.request_call(x, "DOWN"), width=6,
                          bg="lightcoral").pack(side=tk.LEFT, padx=5)
            elif i == 1:
                tk.Button(floor_frame, text="Lên", command=lambda x=i: self.request_call(x, "UP"), width=6,
                          bg="lightgreen").pack(side=tk.LEFT, padx=5)
            else:
                tk.Button(floor_frame, text="Lên", command=lambda x=i: self.request_call(x, "UP"), width=6,
                          bg="lightgreen").pack(side=tk.LEFT, padx=5)
                tk.Button(floor_frame, text="Xuống", command=lambda x=i: self.request_call(x, "DOWN"), width=6,
                          bg="lightcoral").pack(side=tk.LEFT, padx=5)

        self.status2_frame = tk.Frame(self.elevator2_frame, bg="lightblue")
        self.status2_frame.pack(pady=5)
        self.label2_floor = tk.Label(self.status2_frame, text=f"TM2 Tầng: {elevator_system.elevators[1].current_floor}",
                                     font=("Arial", 12), bg="lightblue")
        self.label2_floor.pack()
        self.label2_direction = tk.Label(self.status2_frame,
                                         text=f"TM2 Hướng: {elevator_system.elevators[1].direction}",
                                         font=("Arial", 12), bg="lightblue")
        self.label2_direction.pack()
        self.label2_door = tk.Label(self.status2_frame,
                                    text=f"TM2 Cửa: {'Mở' if elevator_system.elevators[1].door_open else 'Đóng'}",
                                    font=("Arial", 12), bg="lightblue")
        self.label2_door.pack()

        self.canvas2 = tk.Canvas(self.elevator2_frame, width=200, height=550, bg="lightgrey")
        self.canvas2.pack(pady=10)
        self.draw_building(self.canvas2, elevator_system.elevators[1])

        self.select2_frame = tk.Frame(self.elevator2_frame, bg="lightblue")
        self.select2_frame.pack(pady=5)
        tk.Label(self.select2_frame, text="TM2 Chọn tầng", font=("Arial", 12), bg="lightblue").pack()
        row1 = tk.Frame(self.select2_frame, bg="lightblue")
        row1.pack()
        row2 = tk.Frame(self.select2_frame, bg="lightblue")
        row2.pack()
        for i in range(20, 10, -1):
            button_color = "yellow" if i in [18, 19, 20] else "white"
            tk.Button(row1, text=f"T{i}", command=lambda x=i: self.request_floor(elevator_system.elevators[1], x),
                      width=4, bg=button_color).pack(side=tk.LEFT, padx=2)
        for i in range(10, 0, -1):
            tk.Button(row2, text=f"T{i}", command=lambda x=i: self.request_floor(elevator_system.elevators[1], x),
                      width=4).pack(side=tk.LEFT, padx=2)

        tk.Button(self.control_frame, text="Dừng khẩn cấp tất cả", command=self.emergency_stop_all, bg="red",
                  fg="white", font=("Arial", 12), width=20).pack(pady=10)

        self.update_gui()

    def draw_building(self, canvas, elevator):
        floor_height = 550 // elevator.num_floors
        for i in range(elevator.num_floors + 1):
            y = i * floor_height
            canvas.create_line(10, y, 190, y, fill="black")
            if i < elevator.num_floors:
                canvas.create_text(30, y + floor_height // 2, text=f"T{elevator.num_floors - i}", font=("Arial", 8))
        elevator_height = floor_height - 5
        elevator_width = 50
        y_position = (elevator.num_floors - elevator.current_floor) * floor_height + 5
        # Lưu màu gốc của thang máy vào thuộc tính elevator
        elevator.original_color = "blue" if elevator.id == 1 else "green"
        elevator.elevator_rect = canvas.create_rectangle(
            100, y_position, 100 + elevator_width, y_position + elevator_height,
            fill=elevator.original_color, outline="black"
        )

    def update_elevator_position(self, elevator, canvas):
        floor_height = 550 // elevator.num_floors
        elevator_height = floor_height - 5
        y_position = (elevator.num_floors - elevator.current_floor) * floor_height + 5
        # Cập nhật vị trí hình chữ nhật
        canvas.coords(elevator.elevator_rect, 100, y_position, 150, y_position + elevator_height)
        # Thay đổi màu dựa trên trạng thái cửa
        if elevator.door_open:
            canvas.itemconfig(elevator.elevator_rect, fill="white")
        else:
            canvas.itemconfig(elevator.elevator_rect, fill=elevator.original_color)

    def request_call(self, floor, direction):
        self.call_elevator(floor, direction)

    def request_floor(self, elevator, floor):
        if floor in [18, 19, 20] and floor != elevator.current_floor:
            self.show_password_dialog(floor, None, lambda f, d: self.select_floor(elevator, f))
        else:
            self.select_floor(elevator, floor)

    def show_password_dialog(self, floor, direction, callback):
        password_window = Toplevel(self.root)
        password_window.title(f"Nhập mật khẩu cho tầng {floor}")
        password_window.resizable(False, False)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width - 300) // 2
        y_position = (screen_height - 350) // 2
        password_window.geometry(f"300x350+{x_position}+{y_position}")
        Label(password_window, text=f"Vui lòng nhập mật khẩu cho tầng {floor}:", font=("Arial", 12)).pack(pady=10)
        password_entry = Entry(password_window, show="*")
        password_entry.pack(pady=10)
        numpad_frame = tk.Frame(password_window)
        numpad_frame.pack(pady=10)

        # Biến tạm để lưu chuỗi mật khẩu
        current_password = ""

        def add_number(num):
            nonlocal current_password
            current_password += str(num)
            password_entry.delete(0, tk.END)
            password_entry.insert(0, current_password)

        def delete_last():
            nonlocal current_password
            if current_password:
                current_password = current_password[:-1]
                password_entry.delete(0, tk.END)
                password_entry.insert(0, current_password)

        for i in range(1, 10):
            tk.Button(numpad_frame, text=str(i), width=5, command=lambda x=i: add_number(x)).grid(row=(i-1)//3, column=(i-1)%3, padx=5, pady=5)
        tk.Button(numpad_frame, text="0", width=5, command=lambda: add_number(0)).grid(row=3, column=1, padx=5, pady=5)
        tk.Button(numpad_frame, text="Xóa", width=5, command=delete_last).grid(row=3, column=2, padx=5, pady=5)

        button_frame = tk.Frame(password_window)
        button_frame.pack(pady=10)

        def on_submit():
            nonlocal current_password
            if {18: "181818", 19: "191919", 20: "202020"}[floor] == current_password:
                password_window.destroy()
                callback(floor, direction)
            else:
                messagebox.showerror("Lỗi", "Mật khẩu không đúng!")
                password_entry.delete(0, tk.END)
                # Reset mật khẩu
                current_password = ""

        def on_cancel():
            nonlocal current_password
            password_window.destroy()
            current_password = ""  # Reset mật khẩu khi hủy

        tk.Button(button_frame, text="Xác nhận", command=on_submit, bg="lightgreen").pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Hủy", command=on_cancel, bg="lightcoral").pack(side=tk.LEFT, padx=10)

    def call_elevator(self, floor, direction):
        if self.elevator_system.assign_request(floor, direction):
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.requests.append((floor, direction, None, timestamp))  # Không cần assigned_elevator vì không hiển thị
            if len(self.requests) > 20:
                self.requests.pop(0)
            messagebox.showinfo("Yêu cầu", f"Gọi thang tại tầng {floor} ({direction})")
        else:
            messagebox.showerror("Lỗi", "Yêu cầu không hợp lệ!")

    def select_floor(self, elevator, floor):
        if elevator.add_request(floor):
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.requests.append((floor, "INSIDE", elevator.id, timestamp))
            if len(self.requests) > 20:
                self.requests.pop(0)
            messagebox.showinfo("Yêu cầu", f"Thang {elevator.id} chọn tầng {floor}")
        else:
            messagebox.showerror("Lỗi", "Yêu cầu không hợp lệ!")

    def emergency_stop_all(self):
        for elevator in self.elevator_system.elevators:
            elevator.stop()
        messagebox.showinfo("Khẩn cấp", "Cả hai thang máy đã dừng!")
        self.root.quit()

    def update_gui(self):
        self.label1_floor.config(text=f"TM1 Tầng: {self.elevator_system.elevators[0].current_floor}")
        self.label1_direction.config(text=f"TM1 Hướng: {self.elevator_system.elevators[0].direction}")
        self.label1_door.config(text=f"TM1 Cửa: {'Mở' if self.elevator_system.elevators[0].door_open else 'Đóng'}")
        self.update_elevator_position(self.elevator_system.elevators[0], self.canvas1)

        self.label2_floor.config(text=f"TM2 Tầng: {self.elevator_system.elevators[1].current_floor}")
        self.label2_direction.config(text=f"TM2 Hướng: {self.elevator_system.elevators[1].direction}")
        self.label2_door.config(text=f"TM2 Cửa: {'Mở' if self.elevator_system.elevators[1].door_open else 'Đóng'}")
        self.update_elevator_position(self.elevator_system.elevators[1], self.canvas2)

        self.root.after(500, self.update_gui)

if __name__ == "__main__":
    root = tk.Tk()
    elevator_system = ElevatorSystem(num_floors=20)
    gui = ElevatorGUI(root, elevator_system)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Chương trình đã dừng bởi người dùng.")
        root.destroy()
        print("Đã thoát chương trình.")