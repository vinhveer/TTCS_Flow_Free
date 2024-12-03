import random
from PyQt5.QtGui import QColor

class GridData:
    def __init__(self, size=5, difficulty='hard'):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.path_grid = [[0 for _ in range(size)] for _ in range(size)]
        
        self.color_map = {
            1: QColor(231, 76, 60),     # Đỏ
            2: QColor(46, 204, 113),    # Xanh lá
            3: QColor(52, 152, 219),    # Xanh dương
            4: QColor(241, 196, 15),    # Vàng
            5: QColor(155, 89, 182),    # Tím
            6: QColor(26, 188, 156),    # Ngọc lam
            7: QColor(230, 126, 34),    # Cam
            8: QColor(142, 68, 173),    # Tím đậm
            9: QColor(39, 174, 96),     # Xanh lá đậm
            10: QColor(41, 128, 185),   # Xanh dương đậm
            11: QColor(243, 156, 18),   # Vàng cam
            12: QColor(211, 84, 0),     # Nâu đỏ
            13: QColor(192, 57, 43),    # Đỏ đậm
            14: QColor(93, 173, 226),   # Xanh nhạt
            15: QColor(72, 201, 176)    # Xanh ngọc
        }
        
        self.set_difficulty(difficulty)
    
    def set_difficulty(self, difficulty):
        """Cài đặt độ khó của màn chơi"""
        if difficulty == 'easy':
            self.max_colors = 3
            self.size = 5
        elif difficulty == 'medium':
            self.max_colors = 5
            self.size = 6
        elif difficulty == 'hard':
            self.max_colors = 6
            self.size = 7
        else:
            self.max_colors = 4
            self.size = 5
        
        # Cập nhật lại lưới
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.path_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
    
    def random_generate(self):
        # Reset lại grid
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.path_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        # Lấy tất cả các ô trống
        available_cells = [(r, c) for r in range(self.size) for c in range(self.size)]
        
        # Chọn màu ngẫu nhiên
        possible_colors = list(range(1, 16))  # Sử dụng 15 màu
        used_colors = set()
        
        while available_cells and len(used_colors) < self.max_colors:
            # Chọn màu chưa được sử dụng
            color_number = random.choice([c for c in possible_colors if c not in used_colors])
            
            # Đảm bảo có hai điểm của cùng một màu
            start_points = []
            for _ in range(2):
                if available_cells:
                    cell = random.choice(available_cells)
                    available_cells.remove(cell)
                    self.set_color_point(cell[0], cell[1], color_number)
                    start_points.append(cell)
            
            # Thêm màu vào danh sách các màu đã sử dụng
            used_colors.add(color_number)
        
        # Tạo đường đi cho từng màu
        self.generate_paths()
    
    def generate_paths(self):
        """Tạo đường đi cho tất cả các màu"""
        colors = set(color for row in self.grid for color in row if color != 0)
        
        for color in colors:
            self.generate_path(color)
    
    def generate_path(self, color_number):
        points = [(r, c) for r in range(self.size) for c in range(self.size) 
                  if self.grid[r][c] == color_number]
        
        if len(points) != 2:
            return False
        
        start, end = points
        
        def find_path(start, end):
            visited = set()
            path = []
            
            def dfs(current):
                visited.add(current)
                path.append(current)
                
                if current == end:
                    return True
                
                directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
                
                for dx, dy in directions:
                    next_x, next_y = current[0] + dx, current[1] + dy
                    
                    if (0 <= next_x < self.size and 
                        0 <= next_y < self.size and 
                        (next_x, next_y) not in visited and
                        (self.grid[next_x][next_y] == 0 or 
                         self.grid[next_x][next_y] == color_number)):
                        if dfs((next_x, next_y)):
                            return True
                
                path.pop()
                visited.remove(current)
                return False
            
            if dfs(start):
                return path
            return None
        
        path = find_path(start, end)
        
        if path:
            for point in path:
                self.path_grid[point[0]][point[1]] = color_number
            return True
        
        return False
    
    def set_color_point(self, row, col, color_number):
        if 0 <= row < self.size and 0 <= col < self.size:
            self.grid[row][col] = color_number
            return True
        return False
    
    def get_color_point(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row][col]
        return 0
    
    def clear_path_for_color(self, color_number):
        for r in range(self.size):
            for c in range(self.size):
                if self.path_grid[r][c] == color_number:
                    self.path_grid[r][c] = 0

    def update_path(self, row, col, color_number):
        if 0 <= row < self.size and 0 <= col < self.size:
            # Kiểm tra điều kiện không chạm điểm khác màu
            if (self.grid[row][col] != 0 and
                self.grid[row][col] != color_number):
                return False
           
            self.path_grid[row][col] = color_number
            return True
        return False
    
    def is_endpoint(self, row, col, color_number):
        """Kiểm tra xem điểm có phải là điểm đích của màu này không"""
        if 0 <= row < self.size and 0 <= col < self.size:
            return (self.grid[row][col] == color_number and
                    self.path_grid[row][col] == 0)
        return False

    def get_color(self, color_number):
        return self.color_map.get(color_number, QColor(200, 200, 200))
    


