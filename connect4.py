import copy
import random

class Human_Player:
    def __init__(self, player_num):
        self.player_num = player_num
    def next_move(self, board):
        board.print()
        column = int(input(f"Player {self.player_num} 0-{board.width-1}: "))
        return column

class AI:
    def __init__(self, player_num):
        self.player_num = player_num
    def next_move(self, board):
        vec = [x for row in board.board for x in row]
        return random.randrange(1, board.width+1)

class Board:
    def __init__(self, width, height, num_ai, swap_players):
        self.height = height
        self.width = width
        self.board = [[0 for i in range(width)] for j in range(height)]
        self.last_move = None
        self.num_in_column_count = [0 for i in range(width)]
        if num_ai == 2:
            self.player1 = AI(1)
            self.player2 = AI(2)

        elif num_ai == 1:
            self.player1 = AI(1)
            self.player2 = Human_Player(2)

        elif num_ai == 0:
            self.player1 = Human_Player(1)
            self.player2 = Human_Player(2)

        if swap_players:
            tmp = copy.deepcopy(self.player1)
            self.player1 = copy.deepcopy(self.player2)
            self.player2 = tmp
            
    def run_board(self):
        while self.check_winner() == 0:
            self.make_move(self.player1)
            if self.check_winner() == 0:
                self.make_move(self.player2)
        return self.check_winner()

    def make_move(self, player):
        while True:
            x = player.next_move(self)
            if x in range(0, self.width):
                top_of_column = self.get_top(x)
                if top_of_column >= 0:
                    self.board[top_of_column][x] = player.player_num
                    self.last_move = (top_of_column, x)
                    self.num_in_column_count[x] += 1
                    break

    def get_top(self, column):
        x = self.height - 1 - self.num_in_column_count[column]
        return x

    def print(self):
        print("-"*3*self.width)
        for row in self.board:
            print(row)
        print("-"*3*self.width)

    def check_winner(self):
        if all(c == self.height for c in self.num_in_column_count):
            return -1
        if self.last_move == None:
            return 0
        for i in range(4):
            r = self.check_row(i)
            if r > 0:
                return r
        for i in range(4):
            r = self.check_column(i)
            if r > 0:
                return r
        for i in range(4):
            r = self.check_down_left(i)
            if r > 0:
                return r
        for i in range(4):
            r = self.check_down_right(i)
            if r > 0:
                return r
        return 0

    def check_row(self, i):
        r,c = self.last_move
        cur_val = self.board[r][c]
        if c + 4-i >= self.width:
            return 0
        to_check = [(r, c+j) for j in range(-i,4-i)]
        for k in to_check:
            if self.board[k[0]][k[1]] != cur_val:
                return 0
        return cur_val

    def check_column(self, i):
        r,c = self.last_move
        cur_val = self.board[r][c]
        if r + 4-i > self.height:
            return 0
        to_check = [(r+j, c) for j in range(-i,4-i)]
        for k in to_check:
            if self.board[k[0]][k[1]] != cur_val:
                return 0
        return cur_val

    def check_down_left(self, i):
        r,c = self.last_move
        cur_val = self.board[r][c]
        if c - (4-i) > 0 or r + 4-i > self.height:
            return 0
        to_check = [(r+j, c-j) for j in range(-i,4-i)]
        for k in to_check:
            if self.board[k[0]][k[1]] != cur_val:
                return 0
        return cur_val

    def check_down_right(self, i):
        r,c = self.last_move
        cur_val = self.board[r][c]
        if c + 4-i > self.width or r + 4-i > self.height:
            return 0
        to_check = [(r+j, c+j) for j in range(-i,4-i)]
        for k in to_check:
            if self.board[k[0]][k[1]] != cur_val:
                return 0
        return cur_val

b = Board(7, 6, 2, False)
w = b.run_board()
if w == -1:
    print(f"Game ended in a draw")
else:
    print(f"Winner is player {w}")
b.print()
                

