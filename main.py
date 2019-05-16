import os, copy
import random
import functools
import math
import time

directions = [
    [-1, -1],   # diagonal up-left
    [0, -1],    # up
    [1, -1],    # diagonal up-right
    [1, 0],     # right
    [1, 1],     # diagonal down-right
    [0, 1],     # down
    [-1, 1],    # diagonal down-left
    [-1, 0]     # left
]

WHITE = 'W'
BLACK = 'B'
board_size = 8

MINMAX = 1
ALPHABETA = 2

FUNCTION1 = 1
FUNCTION2 = 2

DEPTH = 6


def setup_board(board):
    for i in range(board_size):
        for j in range(board_size):
            board[i][j] = ' '
    board[3][3] = 'W'
    board[3][4] = 'B'
    board[4][4] = 'W'
    board[4][3] = 'B'


def draw_board(board):
    print("    0     1     2     3     4     5     6     7   ")
    print("  ", end='')
    print("+-----" * board_size, end='')
    print("+")

    for i in range(board_size):
        print(str(i) + " ", end='')
        for j in range(board_size):
            print("|  " + board[i][j] + "  ", end='')
        print("|")
        print("  ", end='')
        print("+-----" * board_size, end='')
        print("+")


def is_inside_board(i, j):
    if i >= board_size or i < 0 or j >= board_size or j < 0:
        return False
    else:
        return True


def eval_board_simple(player, board):
    eval = 0
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] == player.color:
                eval += 1
    return eval

def eval_board_weighted(player, board):
    eval = 0
    for i in range(board_size):
        for j in range(board_size):
            if board[i][j] == player.color:
                if (i == 0 and j == 0) or (i == 0 and j == board_size-1) or \
                        (i == board_size-1 and j == 0) or (i == board_size-1 and j == board_size-1):  # corners
                    eval += 5
                if ((i == 0 or i == board_size-1) and (2 <= j <= board_size-3)) or \
                        ((j == 0 or j == board_size-1) and (2 <= i <= board_size-3)):  # sides
                    eval += 3
                else:  # other parts
                    eval += 1
    return eval


class Player:
    def __init__(self, color):
        self.available_moves = []
        self.score = 2
        self.color = color
        if color == WHITE:
            self.enemy = BLACK
        else:
            self.enemy = WHITE

    def is_enemy(self, board, i, j):
        if board[i][j] == self.enemy:
            return True
        else:
            return False

    def mark_position(self, board, i, j):
        if board[i][j] != ' ':  # if position is not empty
            return False
        num_points = 0
        valid_position = False
        count_dir = -1
        for direct in directions:
            next_i, next_j = i, j
            next_i += direct[0]
            next_j += direct[1]
            if is_inside_board(next_i, next_j) and self.is_enemy(board, next_i, next_j):  # if the position is valid and there's an enemy nearby
                while is_inside_board(next_i, next_j) and self.is_enemy(board, next_i, next_j):
                    next_i += direct[0]
                    next_j += direct[1]

                if is_inside_board(next_i, next_j) and board[next_i][next_j] == self.color:
                    count_dir += 1
                    valid_position = True
                    while [next_i, next_j] != [i, j]:
                        next_i -= direct[0]
                        next_j -= direct[1]
                        num_points += 1
                        board[next_i][next_j] = self.color

        return valid_position, num_points-count_dir
        # return board, numPoints

    def is_position_valid(self, board, i, j):
        if board[i][j] != ' ':  # if position is not empty
            return False

        for direct in directions:
            next_i, next_j = i, j
            next_i += direct[0]
            next_j += direct[1]
            if is_inside_board(next_i, next_j) and self.is_enemy(board, next_i, next_j):  # if the position is valid and there's an enemy nearby
                while is_inside_board(next_i, next_j) and self.is_enemy(board, next_i, next_j):
                    next_i += direct[0]
                    next_j += direct[1]
                if is_inside_board(next_i, next_j) and board[next_i][next_j] == self.color:
                    return True
        return False

    def check_game_over(self, board):
        for i in range(board_size):
            for j in range(board_size):
                if self.is_position_valid(board, i, j):
                    return False
        return True

    def update_scores(self, enemy, score):
        self.score += score
        enemy.score -= score - 1

    def check_available_moves(self, board):
        available_moves = []
        for i in range(board_size):
            for j in range(board_size):
                if self.is_position_valid(board, i, j):
                    available_moves.append([i, j])
        self.available_moves = available_moves
        return available_moves

    def make_random_move(self, board):
        self.available_moves = self.check_available_moves(board)
        pos = random.randrange(0, len(self.available_moves))
        i, j = self.available_moves[pos][0], self.available_moves[pos][1]
        valid_pos, score = self.mark_position(board, i, j)
        return valid_pos, score, i, j

    # self.board = Board()
    # self.players = [Player(WHITE), Player(BLACK)]


def min_max(board, player, opponent, depth, is_max, eval_function):
    # if depth == 0:  # if reached the end of the search or if there's no more moves
    #     return eval_function(player, board), None

    # if player.check_game_over(board):
    #     return eval_function(player, board), None

    # best_move = None

    if is_max:
        if depth == 0:  # if reached the end of the search or if there's no more moves
            return eval_function(player, board), None

        if player.check_game_over(board):
            return eval_function(player, board), None

        best_move = None

        best_score = -1  # min possible value
        moves = player.check_available_moves(board)
        for (i, j) in moves:
            temp_board = copy.deepcopy(board)
            player.mark_position(temp_board, i, j)
            score = min_max(temp_board, opponent, player, depth-1, False, eval_function)[0]
            if score > best_score:
                best_score = score
                best_move = [i, j]

    else:
        if depth == 0:  # if reached the end of the search or if there's no more moves
            return eval_function(opponent, board), None

        if player.check_game_over(board):
            return eval_function(opponent, board), None

        best_move = None
        best_score = 105  # max possible value
        moves = player.check_available_moves(board)
        for (i, j) in moves:
            temp_board = copy.deepcopy(board)
            player.mark_position(temp_board, i, j)
            score = min_max(temp_board, opponent, player, depth - 1, True, eval_function)[0]
            if score < best_score:
                best_score = score
                best_move = [i, j]

    return best_score, best_move


def alpha_beta(board, player, opponent, depth, is_max, eval_function, alpha, beta):
    # if depth == 0:  # if reached the end of the search or if there's no more moves
    #    return eval_function(player, board), None

    # if player.check_game_over(board):
    #     return eval_function(player, board), None

    # best_move = None
    if is_max:
        if depth == 0:  # if reached the end of the search or if there's no more moves
            return eval_function(player, board), None

        if player.check_game_over(board):
            return eval_function(player, board), None

        best_move = None
        best_score = -1  # min possible value
        moves = player.check_available_moves(board)
        for (i, j) in moves:
            temp_board = copy.deepcopy(board)
            player.mark_position(temp_board, i, j)
            score = alpha_beta(temp_board, opponent, player, depth-1, False, eval_function, alpha, beta)[0]
            if score > best_score:
                best_score = score
                best_move = [i, j]
            if best_score >= beta:
                return best_score, best_move
            alpha = max(alpha, best_score)

    else:
        if depth == 0:  # if reached the end of the search or if there's no more moves
            return eval_function(opponent, board), None

        if player.check_game_over(board):
            return eval_function(opponent, board), None

        best_move = None
        best_score = 105  # max possible value
        moves = player.check_available_moves(board)
        for (i, j) in moves:
            temp_board = copy.deepcopy(board)
            player.mark_position(temp_board, i, j)
            score = alpha_beta(temp_board, opponent, player, depth - 1, True, eval_function, alpha, beta)[0]
            if score < best_score:
                best_score = score
                best_move = [i, j]
            if best_score <= alpha:
                return best_score, best_move
            beta = min(beta, best_score)

    return best_score, best_move


def is_game_over(board, player):
    return player.check_game_over(board)


def print_menu():
    print("REVERSI - MinMax")
    print("Choose your game mode: ")
    print("1 - Random")
    print("2 - MinMax")
    print("3 - AlphaBeta")
    game_mode = int(input())

    print("Go first? ")
    print("1 - Yes")
    print("2 - No")
    player_color = int(input())

    return player_color-1, game_mode


def play_game_human_ia(board, players, player_color, game_mode):
    turn = 0

    while not is_game_over(board, players[turn]):  # while the current player still can make a move

        print(players[turn].color + " turn! ", end='')

        if turn == player_color:
            i, j = [int(x) for x in input("Select your position (line column): ").split()]

            while True:
                valid_move, score = players[turn].mark_position(board, i, j)
                if valid_move:
                    players[turn].update_scores(players[(turn + 1) % 2], score)
                    break
                else:
                    i, j = [int(x) for x in input("Invalid position! Select again (line column): ").split()]

        else:
            if game_mode == 1:  # random play
                valid_move, score, i, j = players[turn].make_random_move(board)
                print("Selected postion (" + str(i) + ", " + str(j) + ")")
                players[turn].update_scores(players[(turn + 1) % 2], score)

            elif game_mode == 2:  # minmax
                score, move = min_max(board, players[turn], players[(turn + 1) % 2], 4, True, players[0].eval_board_simple)
                print("Selected postion (" + str(move[0]) + ", " + str(move[1]) + ")")
                valid_move, score = players[turn].mark_position(board, move[0], move[1])
                players[turn].update_scores(players[(turn + 1) % 2], score)

            elif game_mode == 3:  # alpha-beta
                score, move = alpha_beta(board, players[turn], players[(turn + 1) % 2], 4, True,
                                      players[0].eval_board_simple, int("-inf"), int("inf"))
                print("Selected postion (" + str(move[0]) + ", " + str(move[1]) + ")")
                valid_move, score = players[turn].mark_position(board, move[0], move[1])
                players[turn].update_scores(players[(turn + 1) % 2], score)

        draw_board(board)
        print("Whites: " + str(players[0].score))
        print("Blacks: " + str(players[1].score))

        turn = (turn + 1) % 2

    input("Press any key to continue...")


def play_game_ia_ia(board, players, game_mode_1, game_mode_2, eval_fn_1, eval_fn_2):
    turn = 0
    eval_func_1 = None
    eval_func_2 = None
    total_time_1 = 0
    total_time_2 = 0

    if eval_fn_1 == FUNCTION1:
        eval_func_1 = functools.partial(eval_board_simple)
    elif eval_fn_1 == FUNCTION2:
        eval_func_1 = functools.partial(eval_board_weighted)

    if eval_fn_2 == FUNCTION1:
        eval_func_2 = functools.partial(eval_board_simple)
    elif eval_fn_2 == FUNCTION2:
        eval_func_2 = functools.partial(eval_board_weighted)

    while not is_game_over(board, players[turn]):  # while the current player still can make a move

        print(players[turn].color + " turn! ", end='')
        start_time = time.time()
        if turn == 0:
            if game_mode_1 == 1:  # random play
                valid_move, score, i, j = players[turn].make_random_move(board)
                end_time = time.time()
                total_time_1 += (end_time-start_time)
                print("Selected postion (" + str(i) + ", " + str(j) + ") " + "in " + str(end_time-start_time) + "s.")
                players[turn].update_scores(players[(turn + 1) % 2], score)

            elif game_mode_1 == 2:  # minmax
                score, move = min_max(board, players[turn], players[(turn + 1) % 2], DEPTH, True,
                                      eval_func_1)
                end_time = time.time()
                total_time_1 += (end_time - start_time)
                print("Selected postion (" + str(move[0]) + ", " + str(move[1]) + ") " + "in " +
                      str(end_time - start_time) + "s.")
                valid_move, score_2 = players[turn].mark_position(board, move[0], move[1])
                players[turn].update_scores(players[(turn + 1) % 2], score_2)

            elif game_mode_1 == 3:  # alpha-beta
                score, move = alpha_beta(board, players[turn], players[(turn + 1) % 2], DEPTH, True,
                                         eval_func_1, float("-inf"), float("inf"))

                end_time = time.time()
                total_time_1 += (end_time - start_time)
                print("Selected postion (" + str(move[0]) + ", " + str(move[1]) + ") " + "in " +
                      str(end_time - start_time) + "s.")
                valid_move, score_2 = players[turn].mark_position(board, move[0], move[1])
                players[turn].update_scores(players[(turn + 1) % 2], score_2)


        else:
            if game_mode_2 == 1:  # random play
                valid_move, score, i, j = players[turn].make_random_move(board)
                end_time = time.time()
                total_time_2 += (end_time - start_time)
                print("Selected postion (" + str(i) + ", " + str(j) + ")")
                players[turn].update_scores(players[(turn + 1) % 2], score)

            elif game_mode_2 == 2:  # minmax
                score, move = min_max(board, players[turn], players[(turn + 1) % 2], DEPTH, True,
                                      eval_func_2)
                end_time = time.time()
                total_time_2 += (end_time - start_time)
                print("Selected postion (" + str(move[0]) + ", " + str(move[1]) + ") " + "in " +
                      str(end_time - start_time) + "s.")
                valid_move, score_2 = players[turn].mark_position(board, move[0], move[1])
                players[turn].update_scores(players[(turn + 1) % 2], score_2)

            elif game_mode_2 == 3:  # alpha-beta
                score, move = alpha_beta(board, players[turn], players[(turn + 1) % 2], DEPTH, True,
                                         eval_func_2, float("-inf"), float("inf"))
                end_time = time.time()
                total_time_2 += (end_time - start_time)
                print("Selected postion (" + str(move[0]) + ", " + str(move[1]) + ") " + "in " +
                      str(end_time - start_time) + "s.")
                valid_move, score_2 = players[turn].mark_position(board, move[0], move[1])
                players[turn].update_scores(players[(turn + 1) % 2], score_2)


        draw_board(board)
        print("Whites: " + str(players[0].score))
        print("Blacks: " + str(players[1].score))

        turn = (turn + 1) % 2
    print("Player 1 time: " + str(total_time_1) + "s")
    print("Player 2 time: " + str(total_time_2) + "s")
    # input("Press any key to continue...")

    return (players[0].score > players[1].score), [total_time_1, total_time_2]


if __name__ == '__main__':
    main_board = [[' ' for i in range(board_size)] for j in range(board_size)]

    player_color, game_mode = 1, 2

    # player_color, game_mode = print_menu()

    setup_board(main_board)
    draw_board(main_board)
    turn = 0

    players = [Player(WHITE), Player(BLACK)]
    winner_matrix = [[0 for i in range(4)] for j in range(4)]
    time_matrix = [[0 for i in range(4)] for j in range(4)]

    for i in range(2):
        for j in range(2):
            winner_matrix[i][j], time_matrix[i][j] = play_game_ia_ia(main_board, players, 2, 2, i+1, j+1)
            setup_board(main_board)

    for i in range(2):
        for j in range(2, 4):
            winner_matrix[i][j], time_matrix[i][j] = play_game_ia_ia(main_board, players, 2, 3, i+1, j+1 - 2)
            setup_board(main_board)
            players = [Player(WHITE), Player(BLACK)]

    for i in range(2, 4):
        for j in range(2):
            winner_matrix[i][j], time_matrix[i][j] = play_game_ia_ia(main_board, players, 3, 2, i+1 - 2, j+1)
            setup_board(main_board)
            players = [Player(WHITE), Player(BLACK)]

    for i in range(2, 4):
        for j in range(2, 4):
            winner_matrix[i][j], time_matrix[i][j] = play_game_ia_ia(main_board, players, 3, 3, i+1 - 2, j+1 - 2)
            setup_board(main_board)
            players = [Player(WHITE), Player(BLACK)]

    print(winner_matrix)
    print(time_matrix)
    #  play_game_human_ia(main_board, players, player_color, game_mode)