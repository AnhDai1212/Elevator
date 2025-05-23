import tkinter as tk
from tkinter import messagebox
import threading
import time
import queue

class Elevator:
    def __init__(self, num_floors, id):
        self.num_floors = num_floors
        self.current_floor = 1
        self.direction = "IDLE"
        self.door_open = False
        self.requests = queue.PriorityQueue()
        self.lock = threading.Lock()
        self.running = True
        self.id = id
        # Biến thống kê
        self.request_count = 0  # Số yêu cầu đã xử lý
        self.stop_count = 0     # Số lần dừng
        self.total_travel_time = 0  # Tổng thời gian di chuyển (giây)

    def add_request(self, floor, direction=None):
        if floor < 1 or floor > self.num_floors:
            return False
        if direction not in [None, "UP", "DOWN"]:
            return False
        with self.lock:
            temp_requests = []
            duplicate = False
            while not self.requests.empty():
                f, d = self.requests.get()
                if f == floor and d == direction:
                    duplicate = True
                temp_requests.append((f, d))
            for req in temp_requests:
                self.requests.put(req)
            if not duplicate:
                self.requests.put((floor, direction))
            if self.direction == "IDLE" and self.running:
                threading.Thread(target=self.process_requests, daemon=True).start()
        return True

    def process_requests(self):
        while self.running and not self.requests.empty():
            with self.lock:
                all_requests = []
                while not self.requests.empty():
                    all_requests.append(self.requests.get())
                target_floor = None
                target_direction = None
                for floor, direction in all_requests:
                    if self.direction == "IDLE":
                        target_floor, target_direction = floor, direction
                        break
                    elif self.direction == "UP" and floor >= self.current_floor and (direction is None or direction == "UP"):
                        if target_floor is None or floor > target_floor:
                            target_floor, target_direction = floor, direction
                    elif self.direction == "DOWN" and floor <= self.current_floor and (direction is None or direction == "DOWN"):
                        if target_floor is None or floor < target_floor:
                            target_floor, target_direction = floor, direction
                for floor, direction in all_requests:
                    if (floor, direction) != (target_floor, target_direction):
                        self.requests.put((floor, direction))
                if target_floor is None:
                    self.direction = "DOWN" if self.direction == "UP" else "UP"
                    continue
                self.direction = "UP" if target_floor > self.current_floor else "DOWN"

            step = 1 if self.direction == "UP" else -1
            while self.current_floor != target_floor and self.running:
                time.sleep(2)  # 2 giây mỗi tầng
                with self.lock:
                    self.current_floor += step
                    self.total_travel_time += 2  # Cộng thời gian di chuyển
                    temp_requests = []
                    stop_here = False
                    while not self.requests.empty():
                        f, d = self.requests.get()
                        if f == self.current_floor and (d is None or d == self.direction):
                            stop_here = True
                        else:
                            temp_requests.append((f, d))
                    for req in temp_requests:
                        self.requests.put(req)
                    if stop_here:
                        self.door_open = True
                        time.sleep(2)
                        self.door_open = False
                        self.stop_count += 1  # Tăng số lần dừng ở tầng trung gian

            with self.lock:
                self.door_open = True
            time.sleep(2)
            with self.lock:
                self.door_open = False
                self.stop_count += 1  # Tăng số lần dừng ở tầng đích
                self.request_count += 1  # Tăng số yêu cầu đã xử lý

        with self.lock:
            self.direction = "IDLE"

    def stop(self):
        self.running = False

class ElevatorSystem:
    def __init__(self, num_floors):
        self.elevators = [Elevator(num_floors, 1), Elevator(num_floors, 2)]
        self.lock = threading.Lock()

    def assign_request(self, floor, direction=None):
        with self.lock:
            best_elevator = None
            min_distance = float('inf')
            for elevator in self.elevators:
                distance = abs(elevator.current_floor - floor)
                if elevator.direction == "IDLE" and distance < min_distance:
                    best_elevator = elevator
                    min_distance = distance
                elif elevator.direction == "UP" and floor >= elevator.current_floor and direction in [None, "UP"] and distance < min_distance:
                    best_elevator = elevator
                    min_distance = distance
                elif elevator.direction == "DOWN" and floor <= elevator.current_floor and direction in [None, "DOWN"] and distance < min_distance:
                    best_elevator = elevator
                    min_distance = distance

            if best_elevator is None:
                min_requests = float('inf')
                for elevator in self.elevators:
                    with elevator.lock:
                        req_count = elevator.requests.qsize()
                        if req_count < min_requests:
                            best_elevator = elevator
                            min_requests = req_count

            return best_elevator.add_request(floor, direction)

class ElevatorGUI:
    def __init__(self, root, elevator_system):
        self.elevator_system = elevator_system
        self.root = root
        self.root.title("Mô phỏng 2 Thang máy - 20 Tầng")

        # Đặt kích thước cửa sổ và cố định
        window_width = 1150
        window_height = 900
        self.root.geometry(f"{window_width}x{window_height}")

        # Đặt cửa sổ chính giữa màn hình
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Cố định kích thước cửa sổ
        self.root.resizable(False, False)

        # Thiết lập giao diện
        self.root.configure(bg="lightblue")
        self.main_frame = tk.Frame(root, bg="lightblue")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.elevator1_frame = tk.Frame(self.main_frame, bg="lightblue")
        self.elevator1_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.Y)

        self.control_frame = tk.Frame(self.main_frame, bg="lightyellow", relief=tk.RAISED, borderwidth=2)
        self.control_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.Y)

        self.elevator2_frame = tk.Frame(self.main_frame, bg="lightblue")
        self.elevator2_frame.pack(side=tk.LEFT, padx=20, pady=10, fill=tk.Y)

        # Thang máy 1: Trạng thái
        self.status1_frame = tk.Frame(self.elevator1_frame, bg="lightblue")
        self.status1_frame.pack(pady=10)
        self.label1_floor = tk.Label(self.status1_frame, text=f"TM1 Tầng: {elevator_system.elevators[0].current_floor}", font=("Arial", 16), bg="lightblue")
        self.label1_floor.pack()
        self.label1_direction = tk.Label(self.status1_frame, text=f"TM1 Hướng: {elevator_system.elevators[0].direction}", font=("Arial", 14), bg="lightblue")
        self.label1_direction.pack()
        self.label1_door = tk.Label(self.status1_frame, text=f"TM1 Cửa: {'Mở' if elevator_system.elevators[0].door_open else 'Đóng'}", font=("Arial", 14), bg="lightblue")
        self.label1_door.pack()

        # Thang máy 1: Thống kê
        self.stats1_frame = tk.Frame(self.elevator1_frame, bg="lightblue")
        self.stats1_frame.pack(pady=5)
        self.label1_requests = tk.Label(self.stats1_frame, text=f"Yêu cầu xử lý: {elevator_system.elevators[0].request_count}", font=("Arial", 12), bg="lightblue")
        self.label1_requests.pack()
        self.label1_stops = tk.Label(self.stats1_frame, text=f"Số lần dừng: {elevator_system.elevators[0].stop_count}", font=("Arial", 12), bg="lightblue")
        self.label1_stops.pack()
        self.label1_travel_time = tk.Label(self.stats1_frame, text=f"Thời gian di chuyển: {elevator_system.elevators[0].total_travel_time} giây", font=("Arial", 12), bg="lightblue")
        self.label1_travel_time.pack()

        # Thang máy 1: Hình vẽ
        self.canvas1 = tk.Canvas(self.elevator1_frame, width=200, height=550, bg="lightgrey")
        self.canvas1.pack(pady=10)
        self.draw_building(self.canvas1, elevator_system.elevators[0])

        # Thang máy 1: Nút chọn tầng trong (2 hàng)
        self.select1_frame = tk.Frame(self.elevator1_frame, bg="lightblue")
        self.select1_frame.pack(pady=10)
        tk.Label(self.select1_frame, text="TM1 Chọn tầng", font=("Arial", 12), bg="lightblue").pack()
        row1 = tk.Frame(self.select1_frame, bg="lightblue")
        row1.pack()
        row2 = tk.Frame(self.select1_frame, bg="lightblue")
        row2.pack()
        for i in range(20, 10, -1):
            tk.Button(row1, text=f"T{i}", command=lambda x=i: self.select_floor(elevator_system.elevators[0], x), width=4).pack(side=tk.LEFT, padx=2)
        for i in range(10, 0, -1):
            tk.Button(row2, text=f"T{i}", command=lambda x=i: self.select_floor(elevator_system.elevators[0], x), width=4).pack(side=tk.LEFT, padx=2)

        # Điều khiển chung: Nút gọi ngoài
        self.call_frame = tk.Frame(self.control_frame, bg="lightyellow")
        self.call_frame.pack(pady=10)
        tk.Label(self.call_frame, text="Gọi thang ngoài", font=("Arial", 14), bg="lightyellow").pack()
        for i in range(elevator_system.elevators[0].num_floors, 0, -1):
            floor_frame = tk.Frame(self.call_frame, bg="lightyellow")
            floor_frame.pack(pady=2)
            tk.Label(floor_frame, text=f"Tầng {i}", width=8, font=("Arial", 10), bg="lightyellow").pack(side=tk.LEFT)
            # Tầng 20: Chỉ có nút "Xuống"
            if i == elevator_system.elevators[0].num_floors:
                tk.Button(floor_frame, text="Xuống", command=lambda x=i: self.call_elevator(x, "DOWN"), width=6, bg="lightcoral").pack(side=tk.LEFT, padx=5)
            # Tầng 1: Chỉ có nút "Lên"
            elif i == 1:
                tk.Button(floor_frame, text="Lên", command=lambda x=i: self.call_elevator(x, "UP"), width=6, bg="lightgreen").pack(side=tk.LEFT, padx=5)
            # Các tầng khác: Có cả hai nút
            else:
                tk.Button(floor_frame, text="Lên", command=lambda x=i: self.call_elevator(x, "UP"), width=6, bg="lightgreen").pack(side=tk.LEFT, padx=5)
                tk.Button(floor_frame, text="Xuống", command=lambda x=i: self.call_elevator(x, "DOWN"), width=6, bg="lightcoral").pack(side=tk.LEFT, padx=5)

        # Thang máy 2: Trạng thái
        self.status2_frame = tk.Frame(self.elevator2_frame, bg="lightblue")
        self.status2_frame.pack(pady=10)
        self.label2_floor = tk.Label(self.status2_frame, text=f"TM2 Tầng: {elevator_system.elevators[1].current_floor}", font=("Arial", 16), bg="lightblue")
        self.label2_floor.pack()
        self.label2_direction = tk.Label(self.status2_frame, text=f"TM2 Hướng: {elevator_system.elevators[1].direction}", font=("Arial", 14), bg="lightblue")
        self.label2_direction.pack()
        self.label2_door = tk.Label(self.status2_frame, text=f"TM2 Cửa: {'Mở' if elevator_system.elevators[1].door_open else 'Đóng'}", font=("Arial", 14), bg="lightblue")
        self.label2_door.pack()

        # Thang máy 2: Thống kê
        self.stats2_frame = tk.Frame(self.elevator2_frame, bg="lightblue")
        self.stats2_frame.pack(pady=5)
        self.label2_requests = tk.Label(self.stats2_frame, text=f"Yêu cầu xử lý: {elevator_system.elevators[1].request_count}", font=("Arial", 12), bg="lightblue")
        self.label2_requests.pack()
        self.label2_stops = tk.Label(self.stats2_frame, text=f"Số lần dừng: {elevator_system.elevators[1].stop_count}", font=("Arial", 12), bg="lightblue")
        self.label2_stops.pack()
        self.label2_travel_time = tk.Label(self.stats2_frame, text=f"Thời gian di chuyển: {elevator_system.elevators[1].total_travel_time} giây", font=("Arial", 12), bg="lightblue")
        self.label2_travel_time.pack()

        # Thang máy 2: Hình vẽ
        self.canvas2 = tk.Canvas(self.elevator2_frame, width=200, height=550, bg="lightgrey")
        self.canvas2.pack(pady=10)
        self.draw_building(self.canvas2, elevator_system.elevators[1])

        # Thang máy 2: Nút chọn tầng trong (2 hàng)
        self.select2_frame = tk.Frame(self.elevator2_frame, bg="lightblue")
        self.select2_frame.pack(pady=10)
        tk.Label(self.select2_frame, text="TM2 Chọn tầng", font=("Arial", 12), bg="lightblue").pack()
        row1 = tk.Frame(self.select2_frame, bg="lightblue")
        row1.pack()
        row2 = tk.Frame(self.select2_frame, bg="lightblue")
        row2.pack()
        for i in range(20, 10, -1):
            tk.Button(row1, text=f"T{i}", command=lambda x=i: self.select_floor(elevator_system.elevators[1], x), width=4).pack(side=tk.LEFT, padx=2)
        for i in range(10, 0, -1):
            tk.Button(row2, text=f"T{i}", command=lambda x=i: self.select_floor(elevator_system.elevators[1], x), width=4).pack(side=tk.LEFT, padx=2)

        # Nút dừng khẩn cấp cho cả hai
        tk.Button(self.control_frame, text="Dừng khẩn cấp tất cả", command=self.emergency_stop_all, bg="red", fg="white", font=("Arial", 12), width=20).pack(pady=20)

        # Cập nhật GUI
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
        elevator.elevator_rect = canvas.create_rectangle(
            100, y_position, 100 + elevator_width, y_position + elevator_height,
            fill="blue" if elevator.id == 1 else "green", outline="black"
        )

    def update_elevator_position(self, elevator, canvas):
        floor_height = 550 // elevator.num_floors
        elevator_height = floor_height - 5
        y_position = (elevator.num_floors - elevator.current_floor) * floor_height + 5
        canvas.coords(elevator.elevator_rect, 100, y_position, 150, y_position + elevator_height)

    def call_elevator(self, floor, direction):
        if self.elevator_system.assign_request(floor, direction):
            messagebox.showinfo("Yêu cầu", f"Gọi thang tại tầng {floor} ({direction})")
        else:
            messagebox.showerror("Lỗi", "Yêu cầu không hợp lệ!")

    def select_floor(self, elevator, floor):
        if elevator.add_request(floor):
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
        self.label1_requests.config(text=f"Yêu cầu xử lý: {self.elevator_system.elevators[0].request_count}")
        self.label1_stops.config(text=f"Số lần dừng: {self.elevator_system.elevators[0].stop_count}")
        self.label1_travel_time.config(text=f"Thời gian di chuyển: {self.elevator_system.elevators[0].total_travel_time} giây")
        self.update_elevator_position(self.elevator_system.elevators[0], self.canvas1)

        self.label2_floor.config(text=f"TM2 Tầng: {self.elevator_system.elevators[1].current_floor}")
        self.label2_direction.config(text=f"TM2 Hướng: {self.elevator_system.elevators[1].direction}")
        self.label2_door.config(text=f"TM2 Cửa: {'Mở' if self.elevator_system.elevators[1].door_open else 'Đóng'}")
        self.label2_requests.config(text=f"Yêu cầu xử lý: {self.elevator_system.elevators[1].request_count}")
        self.label2_stops.config(text=f"Số lần dừng: {self.elevator_system.elevators[1].stop_count}")
        self.label2_travel_time.config(text=f"Thời gian di chuyển: {self.elevator_system.elevators[1].total_travel_time} giây")
        self.update_elevator_position(self.elevator_system.elevators[1], self.canvas2)

        self.root.after(500, self.update_gui)

if __name__ == "__main__":
    root = tk.Tk()
    elevator_system = ElevatorSystem(num_floors=20)
    gui = ElevatorGUI(root, elevator_system)
    root.mainloop()