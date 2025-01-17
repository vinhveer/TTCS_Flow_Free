from collections import deque

def is_valid(row, col, rows, cols):
    return 0 <= row < rows and 0 <= col < cols

def bfs_matrix(matrix, start_row, start_col, end_row, end_col):
    rows = len(matrix)
    cols = len(matrix[0])
    visited = set()
    queue = deque([(start_row, start_col)])
    visited.add((start_row, start_col))
    
    while queue:
        row, col = queue.popleft()
        
        if row == end_row and col == end_col:
            return True
        
        # Các hướng di chuyển (lên, xuống, trái, phải)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            
            if is_valid(nr, nc, rows, cols) and matrix[nr][nc] == 0 and (nr, nc) not in visited:
                # 0 là đường đi, 1 là tường
                queue.append((nr, nc))
                visited.add((nr, nc))
    
    return False

# Ma trận ví dụ
matrix = [
    [0, 0, 1, 0],
    [1, 0, 0, 1],
    [0, 0, 0, 0],
    [1, 1, 0, 0]
]

# Kiểm tra đường đi
if bfs_matrix(matrix, 0, 0, 3, 3):
    print("\nĐến được đích.")
else:
    print("\nKhông đến được đích.")