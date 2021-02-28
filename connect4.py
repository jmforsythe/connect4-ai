import copy
import random

import numpy as np
from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras.layers import Dense, Activation

HEIGHT = 6
WIDTH = 7

def create_model():
    model = Sequential()
    model.add(Dense(HEIGHT*WIDTH*3, input_shape=(HEIGHT*WIDTH*3,)))
    model.add(Activation("relu"))
    model.add(Dense(HEIGHT*WIDTH))
    model.add(Activation("relu"))
    model.add(Dense(WIDTH))
    model.add(Activation("sigmoid"))
    model.compile(loss='mse', optimizer='adam')
    return model

def crossover(parent1, parent2):
    weights1 = parent1.get_weights()
    weights2 = parent2.get_weights()

    gene = random.randint(0, len(weights1)-1)
    tmp = weights1[gene]
    weights1[gene] = weights2[gene]
    weights2[gene] = tmp

    return [weights1, weights2]

def mutate(model_weights):
    for i in range(len(model_weights)):
        for j in range(len(model_weights[i])):
            if random.random() > 0.8:
                model_weights[i][j] += random.random() - 0.5
    return model_weights

class Human_Player:
    def __init__(self, player_num):
        self.player_num = player_num
    def next_move(self, board):
        board.print()
        column = int(input(f"Player {self.player_num} 0-{board.width-1}: "))
        return column

class AI:
    def __init__(self, player_num, model):
        self.player_num = player_num
        self.model = model
        
    def next_move(self, board):
        vec = [x for row in board.board for x in row]
        player_vec = [x == self.player_num for x in vec]
        opponent_vec = [x == (self.player_num%2)+1 for x in vec]
        blank_vec = [x == 0 for x in vec]
        arr = np.atleast_2d(np.array(player_vec+opponent_vec+blank_vec, dtype=np.bool))
        model_out = list(self.model.predict(arr)[0])
        return model_out.index(max(model_out))

class Board:
    def __init__(self, width, height, player1, player2):
        self.height = height
        self.width = width
        self.board = [[0 for i in range(width)] for j in range(height)]
        self.last_move = None
        self.num_in_column_count = [0 for i in range(width)]
        self.player1 = player1
        self.player2 = player2
            
    def run_board(self):
        while self.check_winner() == 0:
            if self.make_move(self.player1) == -1:
                # Invalid move so draw
                return -1
            if self.check_winner() == 0:
                if self.make_move(self.player2) == -1:
                    # Invalid move so draw
                    return -1
        return self.check_winner()

    def make_move(self, player):
        x = player.next_move(self)
        if x in range(0, self.width):
            top_of_column = self.get_top(x)
            if top_of_column >= 0:
                self.board[top_of_column][x] = player.player_num
                self.last_move = (top_of_column, x)
                self.num_in_column_count[x] += 1
                return 0
        return -1

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
        if c + 4-i > self.width or c - i < 0:
            return 0
        to_check = [(r, c+j) for j in range(-i,4-i)]
        for k in to_check:
            if self.board[k[0]][k[1]] != cur_val:
                return 0
        return cur_val

    def check_column(self, i):
        r,c = self.last_move
        cur_val = self.board[r][c]
        if r + 4-i > self.height or r - i < 0:
            return 0
        to_check = [(r+j, c) for j in range(-i,4-i)]
        for k in to_check:
            if self.board[k[0]][k[1]] != cur_val:
                return 0
        return cur_val

    def check_down_left(self, i):
        r,c = self.last_move
        cur_val = self.board[r][c]
        if c - (4-i) < -1 or c + i >= self.width or r + 4-i > self.height or r - i < 0:
            return 0
        to_check = [(r+j, c-j) for j in range(-i,4-i)]
        for k in to_check:
            if self.board[k[0]][k[1]] != cur_val:
                return 0
        return cur_val

    def check_down_right(self, i):
        r,c = self.last_move
        cur_val = self.board[r][c]
        if c + 4-i > self.width or c - i < 0 or r + 4-i > self.height or r - i < 0:
            return 0
        to_check = [(r+j, c+j) for j in range(-i,4-i)]
        for k in to_check:
            if self.board[k[0]][k[1]] != cur_val:
                return 0
        return cur_val

NUM_GENS = 10
POP_SIZE = 10

p = [create_model() for i in range(POP_SIZE)]
try:
    with open("saved_model.json", "r") as file:
        loaded_model = model_from_json(file.read())
except:
    pass

print("Starting simulations")

first = None

for gen in range(NUM_GENS):
    p_score = [0 for i in range(POP_SIZE)]
    for i in range(POP_SIZE-1):
        print(gen, i)
        for j in range(0,i):
            # player 1 = i, player 2 = j
            game = Board(WIDTH, HEIGHT, AI(1,p[i]), AI(2,p[j]))
            x = game.run_board()
            if x == 1:
                p_score[i] += 1
                p_score[j] -= 1
            if x == 2:
                print(f"generation {gen}, member {j} beat member {i} while player 2")
                game.print()
                p_score[j] += 3
                p_score[i] -= 3

            # player 1 = j, player 2 = i
            game = Board(WIDTH, HEIGHT, AI(1,p[j]), AI(2,p[i]))
            x = game.run_board()
            if x == 1:
                p_score[j] += 1
                p_score[i] -= 1
            if x == 2:
                print(f"generation {gen}, member {i} beat member {j} while player 2")
                game.print()
                p_score[i] += 3
                p_score[j] -= 3
    first = p[p_score.index(max(p_score))]
    p.remove(first)
    second = p[p_score.index(max(p_score))]
    p.append(first)
    crossover_weights = crossover(first, second)
    new_weights = [first.get_weights(), second.get_weights(), crossover_weights[0], crossover_weights[1]]
    for i in range(POP_SIZE // 2):
        new_weights.append(mutate(crossover_weights[0]))
        new_weights.append(mutate(crossover_weights[1]))

    for i in range(POP_SIZE):
        p[i].set_weights(new_weights[i])

with open("model.json", "w") as file:
    file.write(first.to_json())

game = Board(WIDTH, HEIGHT, AI(1,first), Human_Player())
game.run_board()
