import copy
import itertools
import time

class SudokuBoard:
    def __init__(self, board=None):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        if board:
            for i in range(9):
                for j in range(9):
                    self.board[i][j] = board[i][j]
        self.candidates = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
        self.update_candidates()

    def update_candidates(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != 0:
                    self.candidates[i][j] = set()
                else:
                    self.candidates[i][j] = set(range(1, 10))
                    for k in range(9):
                        self.candidates[i][j].discard(self.board[i][k])
                        self.candidates[i][j].discard(self.board[k][j])
                    bi, bj = i // 3 * 3, j // 3 * 3
                    for di in range(3):
                        for dj in range(3):
                            self.candidates[i][j].discard(self.board[bi+di][bj+dj])

    def set_cell(self, row, col, value):
        self.board[row][col] = value
        self.update_candidates()

    def is_solved(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    return False
        return True

    def print_board(self):
        for i in range(9):
            line = ''
            for j in range(9):
                v = self.board[i][j]
                line += str(v) if v != 0 else '.'
                if j in [2, 5]:
                    line += ' | '
                else:
                    line += ' '
            print(line)
            if i in [2, 5]:
                print('------+-------+------')

    def print_candidates(self):
        for i in range(9):
            line = ''
            for j in range(9):
                if self.board[i][j] == 0:
                    line += ''.join(str(x) for x in sorted(self.candidates[i][j])).ljust(9)
                else:
                    line += ' '.ljust(9)
                if j in [2, 5]:
                    line += '|'
            print(line)
            if i in [2, 5]:
                print('-'*32)

    def clone(self):
        return copy.deepcopy(self)

    def find_naked_single(self):
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0 and len(self.candidates[i][j]) == 1:
                    v = next(iter(self.candidates[i][j]))
                    return (i, j, v)
        return None

    def find_hidden_single(self):
        for i in range(9):
            for v in range(1, 10):
                cols = [j for j in range(9) if v in self.candidates[i][j]]
                if len(cols) == 1 and self.board[i][cols[0]] == 0:
                    return (i, cols[0], v, 'row')
        for j in range(9):
            for v in range(1, 10):
                rows = [i for i in range(9) if v in self.candidates[i][j]]
                if len(rows) == 1 and self.board[rows[0]][j] == 0:
                    return (rows[0], j, v, 'col')
        for bi in range(3):
            for bj in range(3):
                cells = []
                for di in range(3):
                    for dj in range(3):
                        i, j = bi*3+di, bj*3+dj
                        cells.append((i, j))
                for v in range(1, 10):
                    places = [(i, j) for (i, j) in cells if v in self.candidates[i][j]]
                    if len(places) == 1 and self.board[places[0][0]][places[0][1]] == 0:
                        return (places[0][0], places[0][1], v, 'box')
        return None

    def find_naked_pairs(self):
        # 行
        for i in range(9):
            pairs = [(j, self.candidates[i][j]) for j in range(9) if len(self.candidates[i][j]) == 2]
            seen = {}
            for j, cand in pairs:
                key = tuple(sorted(cand))
                if key in seen:
                    j2 = seen[key]
                    affected = []
                    for jj in range(9):
                        if jj != j and jj != j2 and not self.board[i][jj] and (self.candidates[i][jj] & set(key)):
                            for v in key:
                                if v in self.candidates[i][jj]:
                                    affected.append((i, jj, v))
                                    self.candidates[i][jj].discard(v)
                    if affected:
                        return ("行", i, [(i, j), (i, j2)], key, affected)
                else:
                    seen[key] = j
        # 列
        for j in range(9):
            pairs = [(i, self.candidates[i][j]) for i in range(9) if len(self.candidates[i][j]) == 2]
            seen = {}
            for i, cand in pairs:
                key = tuple(sorted(cand))
                if key in seen:
                    i2 = seen[key]
                    affected = []
                    for ii in range(9):
                        if ii != i and ii != i2 and not self.board[ii][j] and (self.candidates[ii][j] & set(key)):
                            for v in key:
                                if v in self.candidates[ii][j]:
                                    affected.append((ii, j, v))
                                    self.candidates[ii][j].discard(v)
                    if affected:
                        return ("列", j, [(i, j), (i2, j)], key, affected)
                else:
                    seen[key] = i
        # 宫
        for bi in range(3):
            for bj in range(3):
                cells = []
                for di in range(3):
                    for dj in range(3):
                        i, j = bi*3+di, bj*3+dj
                        if len(self.candidates[i][j]) == 2:
                            cells.append((i, j, tuple(sorted(self.candidates[i][j]))))
                seen = {}
                for idx, (i, j, key) in enumerate(cells):
                    if key in seen:
                        i2, j2, _ = cells[seen[key]]
                        affected = []
                        for di in range(3):
                            for dj in range(3):
                                ii, jj = bi*3+di, bj*3+dj
                                if (ii, jj) != (i, j) and (ii, jj) != (i2, j2) and not self.board[ii][jj] and (self.candidates[ii][jj] & set(key)):
                                    for v in key:
                                        if v in self.candidates[ii][jj]:
                                            affected.append((ii, jj, v))
                                            self.candidates[ii][jj].discard(v)
                        if affected:
                            return ("宫", bi*3+bj, [(i, j), (i2, j2)], key, affected)
                    else:
                        seen[key] = idx
        return None

    def find_hidden_pairs(self):
        # 行
        for i in range(9):
            for a in range(1, 10):
                for b in range(a+1, 10):
                    pos_a = [j for j in range(9) if a in self.candidates[i][j]]
                    pos_b = [j for j in range(9) if b in self.candidates[i][j]]
                    if len(pos_a) == 2 and len(pos_b) == 2 and set(pos_a) == set(pos_b):
                        changed = []
                        for j in pos_a:
                            orig = set(self.candidates[i][j])
                            if orig != set([a, b]):
                                self.candidates[i][j].intersection_update([a, b])
                                changed.append((i, j, orig))
                        if changed:
                            return ("行", i, [(i, j) for j in pos_a], (a, b), changed)
        # 列
        for j in range(9):
            for a in range(1, 10):
                for b in range(a+1, 10):
                    pos_a = [i for i in range(9) if a in self.candidates[i][j]]
                    pos_b = [i for i in range(9) if b in self.candidates[i][j]]
                    if len(pos_a) == 2 and len(pos_b) == 2 and set(pos_a) == set(pos_b):
                        changed = []
                        for i in pos_a:
                            orig = set(self.candidates[i][j])
                            if orig != set([a, b]):
                                self.candidates[i][j].intersection_update([a, b])
                                changed.append((i, j, orig))
                        if changed:
                            return ("列", j, [(i, j) for i in pos_a], (a, b), changed)
        # 宫
        for bi in range(3):
            for bj in range(3):
                cells = [(bi*3+di, bj*3+dj) for di in range(3) for dj in range(3)]
                for a in range(1, 10):
                    for b in range(a+1, 10):
                        pos_a = [(i, j) for (i, j) in cells if a in self.candidates[i][j]]
                        pos_b = [(i, j) for (i, j) in cells if b in self.candidates[i][j]]
                        if len(pos_a) == 2 and len(pos_b) == 2 and set(pos_a) == set(pos_b):
                            changed = []
                            for (i, j) in pos_a:
                                orig = set(self.candidates[i][j])
                                if orig != set([a, b]):
                                    self.candidates[i][j].intersection_update([a, b])
                                    changed.append((i, j, orig))
                            if changed:
                                return ("宫", bi*3+bj, pos_a, (a, b), changed)
        return None
    

    def find_pointing_pairs_triples(self):
        for bi in range(3):
            for bj in range(3):
                cells = [(bi*3+di, bj*3+dj) for di in range(3) for dj in range(3)]
                for v in range(1, 10):
                    positions = [(i, j) for (i, j) in cells if v in self.candidates[i][j]]
                    if not positions:
                        continue
                    rows = set(i for (i, j) in positions)
                    if len(rows) == 1:
                        row = next(iter(rows))
                        affected = []
                        for j2 in range(9):
                            if (row, j2) not in positions and (row//3 == bi and j2//3 == bj):
                                continue
                            if (row, j2) not in positions and v in self.candidates[row][j2] and j2//3 != bj:
                                self.candidates[row][j2].discard(v)
                                affected.append((row, j2))
                        if affected:
                            return (bi*3+bj, v, f"行{row+1}", affected)
                    cols = set(j for (i, j) in positions)
                    if len(cols) == 1:
                        col = next(iter(cols))
                        affected = []
                        for i2 in range(9):
                            if (i2, col) not in positions and (i2//3 == bi and col//3 == bj):
                                continue
                            if (i2, col) not in positions and v in self.candidates[i2][col] and i2//3 != bi:
                                self.candidates[i2][col].discard(v)
                                affected.append((i2, col))
                        if affected:
                            return (bi*3+bj, v, f"列{col+1}", affected)
        return None

    def find_box_line_reduction(self):
        for i in range(9):
            for v in range(1, 10):
                positions = [j for j in range(9) if v in self.candidates[i][j]]
                if not positions:
                    continue
                boxes = set(j//3 for j in positions)
                if len(boxes) == 1:
                    bj = next(iter(boxes))
                    affected = []
                    for di in range(3):
                        for dj in range(3):
                            ii, jj = (i//3)*3+di, bj*3+dj
                            if ii == i:
                                continue
                            if v in self.candidates[ii][jj]:
                                self.candidates[ii][jj].discard(v)
                                affected.append((ii, jj))
                    if affected:
                        return ("行", i, v, affected)
        for j in range(9):
            for v in range(1, 10):
                positions = [i for i in range(9) if v in self.candidates[i][j]]
                if not positions:
                    continue
                boxes = set(i//3 for i in positions)
                if len(boxes) == 1:
                    bi = next(iter(boxes))
                    affected = []
                    for di in range(3):
                        for dj in range(3):
                            ii, jj = bi*3+di, (j//3)*3+dj
                            if jj == j:
                                continue
                            if v in self.candidates[ii][jj]:
                                self.candidates[ii][jj].discard(v)
                                affected.append((ii, jj))
                    if affected:
                        return ("列", j, v, affected)
        return None


    def safe_discard(self, i, j, v):
        """
        安全地从(i,j)格子的候选数中移除v。
        """
        if v in self.candidates[i][j]:
            self.candidates[i][j].discard(v)
            
    def solve_backtrack(self):
        """经典回溯法直接填盘，解出即返回True，否则False。"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    for v in range(1, 10):
                        if self._is_safe(i, j, v):
                            self.board[i][j] = v
                            if self.solve_backtrack():
                                return True
                            self.board[i][j] = 0
                    return False
        return True

    def _is_safe(self, i, j, v):
        """判断v能否填入(i,j)"""
        for k in range(9):
            if self.board[i][k] == v or self.board[k][j] == v:
                return False
        bi, bj = i // 3 * 3, j // 3 * 3
        for di in range(3):
            for dj in range(3):
                if self.board[bi+di][bj+dj] == v:
                    return False
        return True

    def bowmans_bingo_step(self, i, j, v):
        """
        教学分步Bowman's Bingo：假设(i,j)=v，分步推理，记录推理链，遇矛盾则排除候选。
        返回推理链log（list of str）。
        """
        test_board = self.clone()
        step_log = [f"假设第{i+1}行第{j+1}列为{v}"]
        try:
            test_board.set_cell(i, j, v)
        except Exception:
            step_log.append(f"假设直接矛盾，排除原盘面第{i+1}行第{j+1}列的{v}")
            self.candidates[i][j].discard(v)
            return step_log
        while True:
            move = test_board.do_one_step(silent=True, log=step_log)
            if not move:
                break
            # 检查矛盾
            for x in range(9):
                for y in range(9):
                    if test_board.board[x][y] == 0 and not test_board.candidates[x][y]:
                        step_log.append(f"发现第{x+1}行第{y+1}列无候选，矛盾！")
                        self.candidates[i][j].discard(v)
                        step_log.append(f"排除原盘面第{i+1}行第{j+1}列的{v}")
                        return step_log
        if test_board.is_solved():
            step_log.append(f"假设第{i+1}行第{j+1}列为{v}，数独已被解决！")
            test_board.print_board()
            return step_log
        step_log.append(f"假设第{i+1}行第{j+1}列为{v}未发现矛盾，无法排除")
        return step_log

    def do_one_step(self, silent=False, log=None):
        move = self.find_naked_single()
        if move:
            i, j, v = move
            self.set_cell(i, j, v)
            msg = f"Naked Single: 在第{i+1}行第{j+1}列唯一候选为{v}，填写{v}。"
            if not silent:
                print(msg)
            if log is not None:
                log.append(msg)
            return True
        move = self.find_hidden_single()
        if move:
            i, j, v, typ = move
            self.set_cell(i, j, v)
            if typ == 'row':
                msg = f"Hidden Single: {v}在第{i+1}行只出现一次，填写{v}。"
            elif typ == 'col':
                msg = f"Hidden Single: {v}在第{j+1}列只出现一次，填写{v}。"
            elif typ == 'box':
                bi, bj = i // 3, j // 3
                msg = f"Hidden Single: {v}在第{bi*3+1}-{bi*3+3}行,第{bj*3+1}-{bj*3+3}列(宫)只出现一次，填写{v}。"
            else:
                msg = f"Hidden Single: {v}在第{i+1}行第{j+1}列/宫只出现一次，填写{v}。"
            if not silent:
                print(msg)
            if log is not None:
                log.append(msg)
            return True
        move = self.find_naked_pairs()
        if move:
            scope, idx, pos, pair, affected = move
            msg = f"Naked Pairs: {scope}{idx+1} 的格{[(i+1,j+1) for (i,j) in pos]} 仅有候选{pair}，从同{scope}其它格中消除{pair}，影响: {[f'({i+1},{j+1})去除{v}' for (i,j,v) in affected]}"
            if not silent:
                print(msg)
            if log is not None:
                log.append(msg)
            return True
        move = self.find_hidden_pairs()
        if move:
            scope, idx, pos, pair, changed = move
            msg = f"Hidden Pairs: {scope}{idx+1} 的格{[(i+1,j+1) for (i,j) in pos]} 仅保留候选{pair}，原候选: {[f'({i+1},{j+1})原{list(orig)}' for (i,j,orig) in changed]}"
            if not silent:
                print(msg)
            if log is not None:
                log.append(msg)
            return True
        move = self.find_pointing_pairs_triples()
        if move:
            boxidx, v, scope, affected = move
            msg = f"Pointing Pairs/Triples: 宫{boxidx+1}内数字{v}仅在{scope}出现，从该{scope}宫外格子中消除{v}，影响: {[f'({i+1},{j+1})' for (i,j) in affected]}"
            if not silent:
                print(msg)
            if log is not None:
                log.append(msg)
            return True
        move = self.find_box_line_reduction()
        if move:
            scope, idx, v, affected = move
            msg = f"Box/Line Reduction: {scope}{idx+1}内数字{v}仅在同一宫出现，从该宫其它格子中消除{v}，影响: {[f'({i+1},{j+1})' for (i,j) in affected]}"
            if not silent:
                print(msg)
            if log is not None:
                log.append(msg)
            return True
        if log is not None:
            if self.is_solved():
                log.append("数独已解出。")
            else:
                log.append("无可用策略。")
        if not silent:
            if self.is_solved():
                print("数独已解出。")
                self.print_board()
            else:
                print("无可用策略。")
        return False

class SudokuGame:
    def __init__(self):
        self.history = []
        self.board = None

    def save_puzzle(self, filename):
        if not self.board:
            print("请先输入数独题目（input命令）后再保存。")
            return
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for row in self.board.board:
                    f.write(''.join(str(num) if num != 0 else '.' for num in row) + '\n')
            print(f'已保存到 {filename}')
        except Exception as e:
            print(f'保存失败: {e}')

    def load_puzzle(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            if len(lines) < 9:
                print('文件内容不足9行，无法加载。')
                return
            board = []
            for line in lines[:9]:
                row = []
                for ch in line:
                    if ch in '0.':
                        row.append(0)
                    elif ch.isdigit():
                        row.append(int(ch))
                if len(row) != 9:
                    print('文件格式有误。')
                    return
                board.append(row)
            self.board = SudokuBoard(board)
            self.history = []
            print(f'已从 {filename} 加载。')
        except Exception as e:
            print(f'加载失败: {e}')

    def input_puzzle(self):
        print("请输入数独谜题（可一次性粘贴9行，每行9个数字，用0或.表示空格）：")
        lines = []
        while True:
            user_input = input().strip()
            # 支持一次性粘贴全部
            if '\n' in user_input or user_input.count(' ') >= 8 or len(user_input) >= 81:
                # 多行或长字符串
                if '\n' in user_input:
                    lines = [line.strip() for line in user_input.splitlines() if line.strip()]
                elif user_input.count(' ') >= 8:
                    lines = [line.strip() for line in user_input.split(' ') if line.strip()]
                else:
                    # 长字符串，按每9个字符分割
                    lines = [user_input[i*9:(i+1)*9] for i in range(9)]
            else:
                lines.append(user_input)
                while len(lines) < 9:
                    line = input(f"第{len(lines)+1}行: ").strip()
                    lines.append(line)
            if len(lines) != 9:
                print("输入行数不足9行，请重新输入。")
                lines = []
                continue
            board = []
            valid = True
            for line in lines:
                row = []
                for ch in line:
                    if ch in '0.':
                        row.append(0)
                    elif ch.isdigit():
                        row.append(int(ch))
                if len(row) != 9:
                    valid = False
                    break
                board.append(row)
            if not valid:
                print("有行格式不正确，请重新输入。")
                lines = []
                continue
            self.board = SudokuBoard(board)
            self.history = []
            print("谜题输入完成。")
            break

    def show_help(self):
        print("""
可用命令：
 input          输入新的数独题目
 show           显示当前棋盘
 candidates     显示所有格子的候选数
 set r c v      在第r行第c列填入数字v（1-9）
 step           自动应用一步基础策略
 solve          自动求解到不能再用基础策略
 bingo r c v    尝试在第r行第c列填入数字v（1-9），有矛盾则消除第r行第c列的候选数字v,无矛盾且数独已经解决则将解出来的数独显示出来
 undo           撤销上一步
 reset          重新输入谜题
 save 文件名    保存当前数独到文件
 load 文件名    从文件加载数独
 help           显示帮助
 exit           退出程序
        """)

    def require_board(self):
        if not self.board:
            print("请先用 input 命令输入数独题目。")
            return False
        return True

    def run(self):
        self.show_help()
        while True:
            cmd = input("请输入命令(help查看帮助): ").strip().lower()
            if cmd == 'input':
                self.input_puzzle()
            elif cmd == 'show':
                if self.require_board():
                    if self.board and self.board.is_solved():
                        print("数独已解决！")
                    self.board.print_board()
            elif cmd == 'candidates':
                if self.require_board():
                    if self.board and self.board.is_solved():
                        print("数独已解决！")
                    self.board.print_candidates()
            elif cmd.startswith('set '):
                if not self.require_board():
                    continue
                try:
                    _, r, c, v = cmd.split()
                    r, c, v = int(r)-1, int(c)-1, int(v)
                    if not (0 <= r < 9 and 0 <= c < 9 and 1 <= v <= 9):
                        print("输入超出范围！")
                        continue
                    if self.board.board[r][c] != 0:
                        print("该格已填写！")
                        continue
                    self.history.append(self.board.clone())
                    self.board.set_cell(r, c, v)
                    print(f"已在第{r+1}行第{c+1}列填写{v}")
                except Exception as e:
                    print("命令格式错误，应为 set r c v")
            elif cmd == 'step':
                if not self.require_board():
                    continue
                self.history.append(self.board.clone())
                if self.board:
                    self.board.do_one_step()
            elif cmd == 'solve':
                if not self.require_board():
                    continue
                self.history.append(self.board.clone())
                step_count = 0
                while True:
                    changed = self.board.do_one_step(silent=False) if self.board else False
                    if changed:
                        step_count += 1
                        continue
                    print(f'自动推理完成，共{step_count}步。')
                    break
            elif cmd == 'brute':
                if not self.require_board() or not self.board:
                    continue
                import time
                start = time.time()
                board = [row[:] for row in self.board.board]
                # 预处理候选数
                candidates = [[set(range(1, 10)) if board[i][j] == 0 else set() for j in range(9)] for i in range(9)]
                for i in range(9):
                    for j in range(9):
                        if board[i][j]:
                            v = board[i][j]
                            for k in range(9):
                                candidates[i][k].discard(v)
                                candidates[k][j].discard(v)
                            bi, bj = i // 3 * 3, j // 3 * 3
                            for di in range(3):
                                for dj in range(3):
                                    candidates[bi+di][bj+dj].discard(v)
                empties = [(i, j) for i in range(9) for j in range(9) if board[i][j] == 0]
                solutions = []
                def dfs(idx):
                    if len(solutions) > 1:
                        return
                    if idx == len(empties):
                        solutions.append([row[:] for row in board])
                        return
                    # MRV: 找候选数最少的格
                    min_cand, min_pos = 10, -1
                    for k in range(idx, len(empties)):
                        i, j = empties[k]
                        if len(candidates[i][j]) < min_cand:
                            min_cand = len(candidates[i][j])
                            min_pos = k
                    if min_pos != idx:
                        empties[idx], empties[min_pos] = empties[min_pos], empties[idx]
                    i, j = empties[idx]
                    for v in sorted(candidates[i][j]):
                        # 记录影响
                        affected = []
                        board[i][j] = v
                        for k in range(9):
                            if v in candidates[i][k]:
                                candidates[i][k].remove(v)
                                affected.append((i, k))
                            if v in candidates[k][j]:
                                candidates[k][j].remove(v)
                                affected.append((k, j))
                        bi, bj = i // 3 * 3, j // 3 * 3
                        for di in range(3):
                            for dj in range(3):
                                ii, jj = bi+di, bj+dj
                                if v in candidates[ii][jj]:
                                    candidates[ii][jj].remove(v)
                                    affected.append((ii, jj))
                        dfs(idx+1)
                        # 回溯
                        board[i][j] = 0
                        for ii, jj in affected:
                            candidates[ii][jj].add(v)
                    if min_pos != idx:
                        empties[idx], empties[min_pos] = empties[min_pos], empties[idx]
                dfs(0)
                if not solutions:
                    print("无解。耗时{:.3f}s".format(time.time()-start))
                else:
                    print("有解。解如下：")
                    for row in solutions[0]:
                        print(' '.join(str(x) for x in row))
                    if len(solutions) == 1:
                        print("唯一解。", end=' ')
                    else:
                        print("多解。", end=' ')
                    print("耗时{:.3f}s".format(time.time()-start))
            elif cmd == 'undo':
                if not self.require_board():
                    continue
                if self.history:
                    self.board = self.history.pop()
                    print("已撤销上一步。")
                else:
                    print("没有可撤销的操作。")
            elif cmd == 'reset':
                self.board = None
                self.history = []
                print("已重置，等待输入新命令。")
            elif cmd.startswith('save '):
                _, filename = cmd.split(maxsplit=1)
                self.save_puzzle(filename)
            elif cmd.startswith('load '):
                self.load_puzzle(cmd.split(maxsplit=1)[1])
            elif cmd == 'help':
                self.show_help()
            elif cmd == 'exit':
                print("感谢使用，再见！")
                break
            elif cmd.startswith('bingo'):
                parts = cmd.split()
                if len(parts) != 4:
                    print("用法: bingo i j v (i,j为1-9行列，v为候选)")
                    continue
                try:
                    i, j, v = int(parts[1])-1, int(parts[2])-1, int(parts[3])
                    if not (0 <= i < 9 and 0 <= j < 9 and 1 <= v <= 9):
                        print("输入超出范围！")
                        continue
                    if self.board and self.board.board[i][j] != 0:
                        print("该格已填写！")
                        continue
                    if self.board:
                        log = self.board.bowmans_bingo_step(i, j, v)
                        print("\n".join(log))
                except Exception as e:
                    print("命令格式错误，应为 bingo i j v")
            else:
                print("未知命令，请输入help查看帮助。")

if __name__ == '__main__':
    game = SudokuGame()
    game.run()
