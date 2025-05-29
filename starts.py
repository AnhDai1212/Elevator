import sqlite3
import matplotlib

# Đặt backend TkAgg để tránh lỗi với PyCharm
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt

def generate_stats():
    # Kết nối đến database
    db_conn = sqlite3.connect("elevator.db")
    cursor = db_conn.cursor()

    # Truy vấn để đếm tần suất đích đến (floor) của các yêu cầu từ bên trong thang máy (direction = 'NONE')
    cursor.execute("""
        SELECT floor, COUNT(*) as frequency 
        FROM request_history 
        WHERE direction = 'NONE' 
        GROUP BY floor 
        ORDER BY frequency DESC
    """)
    data = cursor.fetchall()

    # Đóng kết nối
    db_conn.close()

    # Tách dữ liệu thành danh sách tầng và tần suất
    floors = [row[0] for row in data]
    frequencies = [row[1] for row in data]

    # Tạo biểu đồ cột
    plt.figure(figsize=(10, 6))
    plt.bar(floors, frequencies, color='skyblue')
    plt.xlabel('Tầng đích')
    plt.ylabel('Tần suất yêu cầu từ bên trong thang máy')
    plt.title('Thống kê tần suất đích đến của thang máy')
    plt.xticks(floors)  # Đảm bảo tất cả tầng được hiển thị trên trục x
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)

    # Tìm tầng có tần suất cao nhất
    if frequencies:  # Kiểm tra xem có dữ liệu không
        max_floor = floors[frequencies.index(max(frequencies))]
        max_freq = max(frequencies)
        plt.text(max_floor, max_freq, f'{max_freq}', ha='center', va='bottom')
        print(f"Tầng đích có tần suất yêu cầu cao nhất từ bên trong thang máy là tầng {max_floor} với {max_freq} lần.")
    else:
        print("Không có dữ liệu yêu cầu từ bên trong thang máy (direction = NONE).")

    # Hiển thị biểu đồ trực tiếp
    plt.show()

if __name__ == "__main__":
    generate_stats()