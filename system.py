from threading import Lock
from elevator import Elevator
import sqlite3

class ElevatorSystem:
    def __init__(self, num_floors):
        self.elevators = [Elevator(num_floors, 1), Elevator(num_floors, 2)]
        self.lock = Lock()
        # Tạo bảng database cho lịch sử request
        self.create_tables()

    def create_tables(self):
        db_conn = sqlite3.connect("elevator.db")
        cursor = db_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS request_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                elevator_id INTEGER,
                floor INTEGER,
                direction TEXT,
                timestamp TEXT
            )
        """)
        db_conn.commit()
        db_conn.close()

    def assign_request(self, floor, direction=None):
        with self.lock:
            best_elevator = None
            for elevator in self.elevators:
                with elevator.lock:
                    if elevator.direction == "IDLE":
                        if best_elevator is None or abs(elevator.current_floor - floor) < abs(best_elevator.current_floor - floor):
                            best_elevator = elevator
                    elif elevator.direction == "UP" and direction in [None, "UP"] and floor >= elevator.current_floor:
                        if best_elevator is None or (floor > elevator.current_floor and abs(floor - elevator.current_floor) < abs(best_elevator.current_floor - floor)):
                            best_elevator = elevator
                    elif elevator.direction == "DOWN" and direction in [None, "DOWN"] and floor <= elevator.current_floor:
                        if best_elevator is None or (floor < elevator.current_floor and abs(floor - elevator.current_floor) < abs(best_elevator.current_floor - floor)):
                            best_elevator = elevator

            if best_elevator is None:
                for elevator in self.elevators:
                    if elevator == self.elevators[0]:
                        best_elevator = elevator
                        break

            if best_elevator and best_elevator.add_request(floor, direction):
                return True
        return False