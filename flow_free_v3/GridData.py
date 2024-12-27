from PyQt5.QtGui import QColor

class GridData:
    def __init__(self):
        self.grid = []
        self.path_grid = []
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
        
        # Khởi tạo với giá trị mặc định
        self.mode = 'hard'
        self.level = '2'
        self.size = None  # Thêm biến size
        self.load_game()  # Tự động load game với mode và level mặc định

    def get_mode(self):
        return self.mode
    
    def get_level(self):
        return self.level
    
    def set_mode(self, mode):
        self.mode = mode
        self.load_game()  # Load lại game khi thay đổi mode

    def set_level(self, level):
        self.level = level
        self.load_game()  # Load lại game khi thay đổi level

    def load_game(self):
        """Load game với mode và level hiện tại"""
        if self.mode and self.level:
            file_path = f"levels/{self.mode}-{self.level}.txt"
            try:
                self.load_from_file(file_path)
            except Exception as e:
                print(f"Error loading game: {e}")

    def load_from_file(self, file_path):
        """Đọc dữ liệu lưới từ file."""
        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                
                # Lấy kích thước từ dòng đầu tiên
                self.size = int(lines[0].strip().split()[0])
                
                # Đọc lưới từ các dòng tiếp theo
                self.grid = [
                    list(map(int, line.strip().split()))
                    for line in lines[1:]
                ]
                
                # Khởi tạo lưới đường đi (path_grid)
                self.path_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]

        except Exception as e:
            raise ValueError(f"Lỗi khi đọc file: {e}")

    def getSize(self):
        """Trả về kích thước lưới."""
        return self.size
    
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
        # Convert QColor to a hashable format if it's a QColor object
        if isinstance(color_number, QColor):
            return color_number
        # Otherwise use the color map as before
        return self.color_map.get(color_number, QColor(200, 200, 200))

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
    
    def clear_all_paths(self):
        """Xóa tất cả các đường đi trong path_grid"""
        self.path_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]

    def get_original_grid(self):
        return [[self.grid[i][j] for j in range(self.size)] for i in range(self.size)]
