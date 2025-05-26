import sqlite3
from datetime import datetime
from threading import Lock
from elevator import Elevator  # Import class Elevator từ file elevator.py


class ElevatorSystem:
    def __init__(self, num_floors):
        self.db_conn = sqlite3.connect("elevator.db")
        self.create_tables()
        self.elevators = [Elevator(num_floors, 1), Elevator(num_floors, 2)]
        self.lock = Lock()

    def create_tables(self):
        cursor = self.db_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                floor INTEGER,
                direction TEXT,
                elevator_id INTEGER,
                timestamp TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS elevator_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                elevator_id INTEGER,
                current_floor INTEGER,
                direction TEXT,
                door_open INTEGER,
                timestamp TEXT
            )
        """)
        self.db_conn.commit()

    def assign_request(self, floor, direction=None):
        with self.lock:
            best_elevator = None
            min_distance = float('inf')
            for elevator in self.elevators:
                distance = abs(elevator.current_floor - floor)
                if elevator.direction == "IDLE" and distance < min_distance:
                    best_elevator = elevator
                    min_distance = distance
                elif elevator.direction == "UP" and floor >= elevator.current_floor and direction in [None,
                                                                                                      "UP"] and distance < min_distance:
                    best_elevator = elevator
                    min_distance = distance
                elif elevator.direction == "DOWN" and floor <= elevator.current_floor and direction in [None,
                                                                                                        "DOWN"] and distance < min_distance:
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

            if best_elevator.add_request(floor, direction):
                cursor = self.db_conn.cursor()
                cursor.execute(
                    "INSERT INTO requests (floor, direction, elevator_id, timestamp) VALUES (?, ?, ?, ?)",
                    (floor, direction if direction else "NONE", best_elevator.id,
                     datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
                self.db_conn.commit()
                return True
        return False