import threading
import time
import queue
import sqlite3
from datetime import datetime


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
        self.request_count = 0
        self.stop_count = 0
        self.total_travel_time = 0

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
        db_conn = sqlite3.connect("elevator.db")
        try:
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
                        elif self.direction == "UP" and floor >= self.current_floor and (
                                direction is None or direction == "UP"):
                            if target_floor is None or floor > target_floor:
                                target_floor, target_direction = floor, direction
                        elif self.direction == "DOWN" and floor <= self.current_floor and (
                                direction is None or direction == "DOWN"):
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
                    time.sleep(2)
                    with self.lock:
                        self.current_floor += step
                        self.total_travel_time += 2
                        self.log_state(db_conn)
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
                            self.log_state(db_conn)
                            time.sleep(2)
                            self.door_open = False
                            self.log_state(db_conn)
                            self.stop_count += 1

                with self.lock:
                    self.door_open = True
                    self.log_state(db_conn)
                time.sleep(2)
                with self.lock:
                    self.door_open = False
                    self.log_state(db_conn)
                    self.stop_count += 1
                    self.request_count += 1

            with self.lock:
                self.direction = "IDLE"
                self.log_state(db_conn)
        finally:
            db_conn.close()

    def log_state(self, db_conn):
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO elevator_states (elevator_id, current_floor, direction, door_open, timestamp) VALUES (?, ?, ?, ?, ?)",
            (self.id, self.current_floor, self.direction, 1 if self.door_open else 0,
             datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        db_conn.commit()