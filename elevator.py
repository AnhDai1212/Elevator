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
        self.id = id  # ID của thang máy (1 hoặc 2)

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
                time.sleep(1)
                with self.lock:
                    self.current_floor += step
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

            with self.lock:
                self.door_open = True
            time.sleep(2)
            with self.lock:
                self.door_open = False

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
            # Tìm thang máy gần nhất và cùng hướng
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

            # Nếu không tìm thấy thang phù hợp, chọn thang ít yêu cầu hơn
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
        self.root.title("Mô phỏng 2 Thang máy")
        self.root.geometry("900x600")  # Tăng chiều rộng cho 2 thang

        # Khung chính: 3 cột
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Cột trái: Thang máy 1
        self.elevator1_frame = tk.Frame(self.main_frame)
        self.elevator1_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Cột giữa: Điều khiển chung
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Cột phải: Thang máy 2
        self.elevator2_frame = tk.Frame(self.main_frame)
        self.elevator2_frame.pack(side=tk.LEFT, padx=10, fill=tk.Y)

        # Thang máy 1: Trạng thái
        self.status1_frame = tk.Frame(self.elevator1_frame)
        self.status1_frame.pack(pady=10)
        self.label1_floor = tk.Label(self.status1_frame, text=f"TM1 Tầng: {elevator_system.elevators[0].current_floor}", font=("Arial", 14))
        self.label1_floor.pack()
        self.label1_direction = tk.Label(self.status1_frame, text=f"TM1 Hướng: {elevator_system.elevators[0].direction}", font=("Arial", 12))
        self.label1_direction.pack()
        self.label1_door = tk.Label(self.status1_frame, text=f"TM1 Cửa: {'Mở' if elevator_system.elevators[0].door_open else 'Đóng'}", font=("Arial", 12))
        self.label1_door.pack()

        # Thang máy 1: Hình vẽ
        self.canvas1 = tk.Canvas(self.elevator1_frame, width=200, height=500, bg="lightgrey")
        self.canvas1.pack(pady=10)
        self.draw_building(self.canvas1, elevator_system.elevators[0])

        # Điều khiển chung: Nút gọi ngoài
        self.call_frame = tk.Frame(self.control_frame)
        self.call_frame.pack(pady=10)
        tk.Label(self.call_frame, text="Gọi thang ngoài", font=("Arial", 12)).pack()
        for i in range(elevator_system.elevators[0].num_floors, 0, -1):
            floor_frame = tk.Frame(self.call_frame)
            floor_frame.pack()
            tk.Label(floor_frame, text=f"Tầng {i}", width=10).pack(side=tk.LEFT)
            tk.Button(floor_frame, text="Lên", command=lambda x=i: self.call_elevator(x, "UP")).pack(side=tk.LEFT, padx=5)
            tk.Button(floor_frame, text="Xuống", command=lambda x=i: self.call_elevator(x, "DOWN")).pack(side=tk.LEFT)

        # Thang máy 2: Trạng thái
        self.status2_frame = tk.Frame(self.elevator2_frame)
        self.status2_frame.pack(pady=10)
        self.label2_floor = tk.Label(self.status2_frame, text=f"TM2 Tầng: {elevator_system.elevators[1].current_floor}", font=("Arial", 14))
        self.label2_floor.pack()
        self.label2_direction = tk.Label(self.status2_frame, text=f"TM2 Hướng: {elevator_system.elevators[1].direction}", font=("Arial", 12))
        self.label2_direction.pack()
        self.label2_door = tk.Label(self.status2_frame, text=f"TM2 Cửa: {'Mở' if elevator_system.elevators[1].door_open else 'Đóng'}", font=("Arial", 12))
        self.label2_door.pack()

        # Thang máy 2: Hình vẽ
        self.canvas2 = tk.Canvas(self.elevator2_frame, width=200, height=500, bg="lightgrey")
        self.canvas2.pack(pady=10)
        self.draw_building(self.canvas2, elevator_system.elevators[1])

        # Nút dừng khẩn cấp cho cả hai
        tk.Button(self.control_frame, text="Dừng khẩn cấp tất cả", command=self.emergency_stop_all, bg="red", fg="white").pack(pady=10)

        # Cập nhật GUI
        self.update_gui()

    def draw_building(self, canvas, elevator):
        floor_height = 500 // elevator.num_floors
        for i in range(elevator.num_floors + 1):
            y = i * floor_height
            canvas.create_line(10, y, 190, y, fill="black")
            if i < elevator.num_floors:
                canvas.create_text(30, y + floor_height // 2, text=f"Tầng {elevator.num_floors - i}", font=("Arial", 10))
        elevator_height = floor_height - 10
        elevator_width = 50
        y_position = (elevator.num_floors - elevator.current_floor) * floor_height + 5
        elevator.elevator_rect = canvas.create_rectangle(
            100, y_position, 100 + elevator_width, y_position + elevator_height,
            fill="blue" if elevator.id == 1 else "green", outline="black"
        )

    def update_elevator_position(self, elevator, canvas):
        floor_height = 500 // elevator.num_floors
        elevator_height = floor_height - 10
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
        self.update_elevator_position(self.elevator_system.elevators[0], self.canvas1)

        self.label2_floor.config(text=f"TM2 Tầng: {self.elevator_system.elevators[1].current_floor}")
        self.label2_direction.config(text=f"TM2 Hướng: {self.elevator_system.elevators[1].direction}")
        self.label2_door.config(text=f"TM2 Cửa: {'Mở' if self.elevator_system.elevators[1].door_open else 'Đóng'}")
        self.update_elevator_position(self.elevator_system.elevators[1], self.canvas2)

        self.root.after(500, self.update_gui)

if __name__ == "__main__":
    root = tk.Tk()
    elevator_system = ElevatorSystem(num_floors=10)
    gui = ElevatorGUI(root, elevator_system)
    # Thêm nút chọn tầng trong cho từng thang
    for i in range(10, 0, -1):
        tk.Button(gui.elevator1_frame, text=f"TM1 T{i}", command=lambda x=i: gui.select_floor(elevator_system.elevators[0], x)).pack(side=tk.LEFT, padx=2)
        tk.Button(gui.elevator2_frame, text=f"TM2 T{i}", command=lambda x=i: gui.select_floor(elevator_system.elevators[1], x)).pack(side=tk.LEFT, padx=2)
    root.mainloop()