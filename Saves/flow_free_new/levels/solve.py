# Constants
import queue
N = 14
BITS = 4
UP, LEFT, DOWN, RIGHT = 1, 2, 4, 8
class State:
    def __init__(self, state=0):
        self.state = state

    def __hash__(self):
        return hash(self.state)

    def __eq__(self, other):
        return isinstance(other, State) and self.state == other.state

    def __lt__(self, other):
        return isinstance(other, State) and self.state < other.state

    def get(self, p):
        return self.state >> ((p - 1) * BITS) & ((1 << BITS) - 1)

    def set(self, p, v):
        self.state &= ~(((1 << BITS) - 1) << ((p - 1) * BITS))
        self.state |= v << ((p - 1) * BITS)
        return self

    def counterpart(self, p):
        if self.get(p) == 1:
            cover = 1
            x = p + 1
            while cover > 0 and x <= 100:
                v = self.get(x)
                if v == 1:
                    cover += 1
                elif v == 2:
                    cover -= 1
                if cover == 0:
                    return x
                x += 1
            raise AssertionError("No counterpart found")
        
        elif self.get(p) == 2:
            cover = 1
            x = p - 1
            while cover > 0 and x >= 0:
                v = self.get(x)
                if v == 2:
                    cover += 1
                elif v == 1:
                    cover -= 1
                if cover == 0:
                    return x
                x -= 1
            raise AssertionError("No counterpart found")
        else:
            raise AssertionError("Invalid position")

def bfs(x, y, col):
    q = queue.Queue()
    q.put((x, y)) 
    color[x][y] = col
    
    while not q.empty():
        x, y = q.get()  
        for i in range(4):
            if (conn[x][y].connection >> i) & 1:  # Kiểm tra bit thứ i
                nx = x + dir[i][0]
                ny = y + dir[i][1]
                if color[nx][ny]:  # Nếu đã có màu thì bỏ qua
                    continue
                color[nx][ny] = col
                q.put((nx, ny))
class Info:
    def __init__(self, connection=0):
        self.connection = connection
        
board = [[0] * (N + 1) for _ in range(N + 1)]
color = [[0] * (N + 1) for _ in range(N + 1)]
conn = [[Info() for _ in range(N + 1)] for _ in range(N + 1)]
h = [{} for _ in range(N * N + 2)]
dir = [[-1, 0], [0, -1], [1, 0], [0, 1]]
if __name__ == "__main__":
    with open("expert-4.txt", "r") as infile, open("output.txt", "w") as outfile:
        # Read n and m
        n, m = map(int, infile.readline().split())
        for i in range(1, n + 1):
            row = list(map(int, infile.readline().split()))
            for j in range(1, m + 1):
                board[i][j] = row[j - 1]
        h[1][State(0)] = (State(0), Info())
        # Trong vòng lặp chính
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                id = (i - 1) * m + j
                for cur_state in list(h[id].keys()):
                    cur = State(cur_state.state)
                    _cur = State(cur_state.state)
                    
                    if j == 1:
                        if cur.get(m + 1) != 0:
                            continue
                        old_state = cur.state
                        cur.state = (cur.state << BITS) & ((1 << ((m + 1) * BITS)) - 1)

                    a = cur.get(j)
                    b = cur.get(j + 1)
                    if board[i][j] == 0:
                        if a == 0 and b == 0:
                            next_state = State(cur.state)
                            next_state.set(j, 1).set(j + 1, 2)
                            h[id + 1][next_state] = (_cur, Info(DOWN | RIGHT))
                        
                        elif a == 0 and b != 0:
                            next_state1 = State(cur.state)
                            h[id + 1][next_state1] = (_cur, Info(UP | RIGHT))
                            
                          
                            next_state2 = State(cur.state)
                            next_state2.set(j, b).set(j + 1, 0)
                            
                            h[id + 1][next_state2] = (_cur, Info(UP | DOWN))
                        
                        elif a != 0 and b == 0:
                          
                            next_state1 = State(cur.state)
                           
                            h[id + 1][next_state1] = (_cur, Info(LEFT | DOWN))
                            
                           
                            next_state2 = State(cur.state)
                            next_state2.set(j, 0).set(j + 1, a)
                            
                            h[id + 1][next_state2] = (_cur, Info(LEFT | RIGHT))
                        elif a == 1 and b == 2:
                            pass 
                        # Trường hợp 1-1
                        elif a == 1 and b == 1:
                            p = cur.counterpart(j + 1)
                            next_state = State(cur.state)
                            next_state.set(j, 0).set(j + 1, 0).set(p, 1)
                            h[id + 1][next_state] = (_cur, Info(LEFT | UP))
                        
                        # Trường hợp 2-2
                        elif a == 2 and b == 2:
                            p = cur.counterpart(j)
                            next_state = State(cur.state)
                            next_state.set(j, 0).set(j + 1, 0).set(p, 2)
                            h[id + 1][next_state] = (_cur, Info(LEFT | UP))
                        
                        # Trường hợp 2-1
                        elif a == 2 and b == 1:
                            next_state = State(cur.state)
                            next_state.set(j, 0).set(j + 1, 0)
                            h[id + 1][next_state] = (_cur, Info(LEFT | UP))
                        
                        # Trường hợp cả hai ô đều > 2
                        elif a > 2 and b > 2:
                            if a == b:
                                next_state = State(cur.state)
                                next_state.set(j, 0).set(j + 1, 0)
                                h[id + 1][next_state] = (_cur, Info(LEFT | UP))
                        
                        # Trường hợp ô đầu > 2, ô sau <= 2
                        elif a > 2 and b <= 2:
                            p = cur.counterpart(j + 1)
                            next_state = State(cur.state)
                            next_state.set(j, 0).set(j + 1, 0).set(p, a)
                            h[id + 1][next_state] = (_cur, Info(LEFT | UP))
                        
                        # Trường hợp ô đầu <= 2, ô sau > 2
                        elif a <= 2 and b > 2:
                            p = cur.counterpart(j)
                            next_state = State(cur.state)
                            next_state.set(j, 0).set(j + 1, 0).set(p, b)
                            h[id + 1][next_state] = (_cur, Info(LEFT | UP))
                        
                        else:
                            raise AssertionError("Invalid state")

                    else:
                        if a == 0 and b == 0:
                            # First state
                            next_state1 = State(cur.state)
                            next_state1.set(j, board[i][j] + 2)
                           
                            h[id + 1][next_state1] = (_cur, Info(DOWN))
                            
                            # Second state
                            next_state2 = State(cur.state)
                            next_state2.set(j + 1, board[i][j] + 2)
                            
                            h[id + 1][next_state2] = (_cur, Info(RIGHT))
                        
                        elif a == 0 and b != 0:
                            if b <= 2:
                                p = cur.counterpart(j + 1)
                                next_state1 = State(cur.state)
                                next_state1.set(j, 0).set(j + 1, 0).set(p, board[i][j] + 2)
                                
                                h[id + 1][next_state1] = (_cur, Info(UP))
                            elif b > 2 and b == board[i][j] + 2:
                                next_state1 = State(cur.state)
                                next_state1.set(j, 0).set(j + 1, 0)
                                
                                h[id + 1][next_state1] = (_cur, Info(UP))
                        
                        elif a != 0 and b == 0:
                            if a <= 2:
                                p = cur.counterpart(j)
                                next_state1 = State(cur.state)
                                next_state1.set(j, 0).set(j + 1, 0).set(p, board[i][j] + 2)
                                
                                h[id + 1][next_state1] = (_cur, Info(LEFT))
                            elif a > 2 and a == board[i][j] + 2:
                                next_state1 = State(cur.state)
                                next_state1.set(j, 0).set(j + 1, 0)
                               
                                h[id + 1][next_state1] = (_cur, Info(LEFT))
        # Kiểm tra xem state 0 có tồn tại trong h[n * m + 1]
        if State(0) in h[n * m + 1]:
            print("Found")
            state = State(0)
            # Truy vết ngược từ cuối về đầu
            for x in range(n, 0, -1):
                for y in range(m, 0, -1):
                    id = (x - 1) * m + y
                    assert state in h[id + 1], f"State not found in h[{id + 1}]"
                    conn[x][y] = h[id + 1][state][1]  # Lấy Info
                    state = h[id + 1][state][0]       # Lấy _cur
            
            # Tô màu cho các ô có số
            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    if board[i][j]:  # Nếu ô có giá trị
                        if not color[i][j]:  # Nếu chưa tô màu
                            bfs(i, j, board[i][j])
                        else:
                            assert board[i][j] == color[i][j], f"Color mismatch at {i},{j}"
            
            # In kết quả
            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    print(color[i][j], end=' ') 
                print()  