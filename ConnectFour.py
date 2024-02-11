# system libs
import argparse
import multiprocessing as mp
import tkinter as tk
import random
# 3rd party libs
import numpy as np
# Local libs
from Player import AIPlayer, RandomPlayer, HumanPlayer

#https://stackoverflow.com/a/37737985
def turn_worker(board, send_end, p_func):
    send_end.send(p_func(board))

class Game:
    def __init__(self, player1, player2, time):
        # resource:
        # https://github.com/DanielSabo/CSE240_Assignments/blob/main/Assignment2/ConnectFour.py
        self.players = [player1, player2]
        self.colors = ['yellow', 'red']
        self.current_turn = 0
        self.board = np.zeros([6,7]).astype(np.uint8)
        self.gui_board = []
        self.game_over = False
        self.run_to_end = False
        self.ai_turn_limit = time
        self.human_move = None
        #https://stackoverflow.com/a/38159672
        self.root = tk.Tk()
        self.root.title('Connect 4')
        self.player_string = tk.Label(self.root, text=player1.player_string)
        self.player_string.pack()
        self.c = tk.Canvas(self.root, width=700, height=600)
        self.c.pack()
        for row in range(0, 700, 100):
            column = []
            for col in range(0, 700, 100):
                column.append(self.c.create_oval(row, col, row+100, col+100, fill=''))
            self.gui_board.append(column)
        self.c.bind("<Button-1>", self.canvas_click)
        self.b_next_move = tk.Button(self.root, text='Next Move', command=self.make_move)
        self.b_finish = tk.Button(self.root, text='Finish Game', command=self.finish_game)
        self.b_reset = tk.Button(self.root, text='Reset Game', command=self.reset_game)
        self.b_next_move.pack()
        if player1.type != 'human' and player2.type != 'human':
            self.b_finish.pack()
        self.b_reset.pack()
        self.root.mainloop()

    def canvas_click(self, e):
        if self.human_move == "move_me":
            # Select the column based on the x value of the mouse click
            self.human_move = e.x//100
            self.make_move()

    def reset_game(self):
        self.current_turn = 0
        self.current_turn = 0
        self.game_over = False
        self.run_to_end = False
        self.human_move = None
        self.board = np.zeros([6,7]).astype(np.uint8)
        for i in self.gui_board:
            for j in i:
                self.c.itemconfig(j, fill='')
        self.b_next_move["state"] = "normal"
        self.b_finish["state"] = "normal"
        self.b_reset["state"] = "normal"

    def finish_game(self):
        self.run_to_end = True
        self.b_next_move["state"] = "disabled"
        self.b_finish["state"] = "disabled"
        self.make_move()

    def print_colored_message(self, player_number):
        # ANSI color codes for colors
        colors = {'red': '\033[91m', 'yellow': '\033[93m', 'end': '\033[0m'}
        # ASCII Art Text for "THE WINNER IS PLAYER X"
        the = """

████████╗██╗  ██╗███████╗
╚══██╔══╝██║  ██║██╔════╝
   ██║   ███████║█████╗
   ██║   ██╔══██║██╔══╝
   ██║   ██║  ██║███████╗
   ╚═╝   ╚═╝  ╚═╝╚══════╝


        """
        winner = """

██╗    ██╗██╗███╗   ██╗███╗   ██╗███████╗██████╗
██║    ██║██║████╗  ██║████╗  ██║██╔════╝██╔══██╗
██║ █╗ ██║██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
██║███╗██║██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
╚███╔███╔╝██║██║ ╚████║██║ ╚████║███████╗██║  ██║
 ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝


        """
        is_ = """

██╗███████╗
██║██╔════╝
██║███████╗
██║╚════██║
██║███████║
╚═╝╚══════╝


        """
        player = """

██████╗ ██╗      █████╗ ██╗   ██╗███████╗██████╗
██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗
██████╔╝██║     ███████║ ╚████╔╝ █████╗  ██████╔╝
██╔═══╝ ██║     ██╔══██║  ╚██╔╝  ██╔══╝  ██╔══██╗
██║     ███████╗██║  ██║   ██║   ███████╗██║  ██║
╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝


        """
        one = """

 ██╗
███║
╚██║
 ██║
 ██║
 ╚═╝


        """

        two = """

██████╗
╚════██╗
 █████╔╝
██╔═══╝
███████╗
╚══════╝


        """
        color = colors['red'] if player_number == 2 else colors['yellow']
        # printing the winner message in color
        print(color)
        print(the)
        print(winner)
        print(is_)
        print(player)
        print(one if player_number == 1 else two)
        print(colors['end'])

    def make_move(self):
        if not self.game_over:
            current_player = self.players[self.current_turn]
            if current_player.type == 'ai':
                if self.players[int(not self.current_turn)].type == 'random':
                    p_func = current_player.get_expectimax_move
                else:
                    p_func = current_player.get_alpha_beta_move
                try:
                    recv_end, send_end = mp.Pipe(False)
                    p = mp.Process(target=turn_worker, args=(self.board, send_end, p_func))
                    p.start()
                    if p.join(self.ai_turn_limit) is None and p.is_alive():
                        p.terminate()
                        raise Exception('Player Exceeded time limit')
                except Exception as e:
                    uh_oh = 'Uh oh.... something is wrong with Player {}'
                    print(uh_oh.format(current_player.player_number))
                    print(e)
                    raise Exception('Game Over')
                move = recv_end.recv()
            # resource:
            # https://github.com/DanielSabo/CSE240_Assignments/blob/main/Assignment2/ConnectFour.py
            elif current_player.type == 'human':
                if isinstance(self.human_move, int):
                    move = self.human_move
                    # Disable the canvas click event
                    self.human_move = None
                else:
                    # Enable the canvas click event
                    self.human_move = "move_me"
                    self.player_string.configure(text='Click a column to select the move for ' + self.players[self.current_turn].player_string)
                    return
            else:
                move = current_player.get_move(self.board)
            if move is not None:
                self.update_board(int(move), current_player.player_number)
            if self.game_completed(current_player.player_number):
                self.game_over = True
                # resource:
                # https://github.com/DanielSabo/CSE240_Assignments/blob/main/Assignment2/ConnectFour.py
                self.run_to_end = False
                # >>>
                # a small addition to announce the winner
                winner_announcement = "The winner is player {}".format(current_player.player_number)
                print(winner_announcement)
                self.print_colored_message(current_player.player_number)  # Print colorful winner announcement
                # >>>
                self.player_string.configure(text=self.players[self.current_turn].player_string + ' wins!')
            else:
                self.current_turn = int(not self.current_turn)
                self.player_string.configure(text=self.players[self.current_turn].player_string)
        # resource:
        # https://github.com/DanielSabo/CSE240_Assignments/blob/main/Assignment2/ConnectFour.py
        if self.game_over:
            self.b_next_move["state"] = "disabled"
            self.b_finish["state"] = "disabled"
            self.b_reset["state"] = "normal"
        if self.run_to_end and not self.game_over:
            self.root.after(1, self.make_move)

    def update_board(self, move, player_num):
        if 0 in self.board[:,move]:
            update_row = -1
            for row in range(1, self.board.shape[0]):
                update_row = -1
                if self.board[row, move] > 0 and self.board[row-1, move] == 0:
                    update_row = row-1
                elif row==self.board.shape[0]-1 and self.board[row, move] == 0:
                    update_row = row
                if update_row >= 0:
                    self.board[update_row, move] = player_num
                    self.c.itemconfig(self.gui_board[move][update_row],
                                      fill=self.colors[self.current_turn])
                    break
        else:
            err = 'Invalid move by player {}. Column {}'.format(player_num, move)
            raise Exception(err)


    def game_completed(self, player_num):
        player_win_str = '{0}{0}{0}{0}'.format(player_num)
        board = self.board
        to_str = lambda a: ''.join(a.astype(str))
        def check_horizontal(b):
            for row in b:
                if player_win_str in to_str(row):
                    return True
            return False

        def check_verticle(b):
            return check_horizontal(b.T)

        def check_diagonal(b):
            for op in [None, np.fliplr]:
                op_board = op(b) if op else b
                # root_diag = np.diagonal(op_board, offset=0).astype(np.int)
                # DeprecationWarning: `np.int` is a deprecated alias for the
                # builtin `int`. To silence this warning, use `int` by itself.
                # Doing this will not modify any behavior and is safe. When
                # replacing `np.int`, you may wish to use e.g. `np.int64` or
                # `np.int32` to specify the precision. If you wish to review
                # your current use, check the release note link for additional
                # information. Deprecated in NumPy 1.20; for more details and
                # guidance: https://numpy.org/devdocs/release/1.20.0-notes.html#deprecations
                # root_diag = np.diagonal(op_board, offset=0).astype(np.int)
                root_diag = np.diagonal(op_board, offset=0).astype(int)
                if player_win_str in to_str(root_diag):
                    return True
                for i in range(1, b.shape[1]-3):
                    for offset in [i, -i]:
                        diag = np.diagonal(op_board, offset=offset)
                        # diag = to_str(diag.astype(np.int))
                        # DeprecationWarning: `np.int` is a deprecated alias for
                        # the builtin `int`. To silence this warning, use `int` by
                        # itself. Doing this will not modify any behavior and is safe.
                        # When replacing `np.int`, you may wish to use e.g. `np.int64`
                        # or `np.int32` to specify the precision. If you wish to review
                        # your current use, check the release note link for additional
                        # information. Deprecated in NumPy 1.20; for more details and
                        # guidance: https://numpy.org/devdocs/release/1.20.0-notes.html#deprecations
                        # diag = to_str(diag.astype(np.int))
                        diag = to_str(diag.astype(int))
                        if player_win_str in diag:
                            return True
            return False
        return (check_horizontal(board) or
                check_verticle(board) or
                check_diagonal(board))

def play_headless_game(player1, player2):
    """
    Plays a headless game between the specified players.
    INPUTS:
    player1 - an object of type AIPlayer, RandomPlayer, or HumanPlayer
    player2 - an object of type AIPlayer, RandomPlayer, or HumanPlayer
    RETURNS:
    The player number (1 or 2) of the winner, or 0 if it's a draw.
    """
    board = np.zeros([6,7])
    current_turn = 0
    game_over = False
    players = [player1, player2]
    while not game_over:
        current_player = players[current_turn]
        opponent_player = players[int(not current_turn)]
        # dynamically determine move based on player types
        if current_player.type == 'ai':
            if opponent_player.type == 'random':
                # print("get_expectimax_move is called")
                move = current_player.get_expectimax_move(board)
            else:
                # print("get_alpha_beta_move is called")
                move = current_player.get_alpha_beta_move(board)
        else:
            move = current_player.get_move(board)
        # the rest of the function remains the same
        if move is not None:
            update_board(board, move, current_player.player_number)
        if game_completed(board, current_player.player_number):
            game_over = True
            return current_player.player_number
        elif np.all(board != 0):
            game_over = True
            return 0  # Draw
        current_turn = 1 - current_turn

def update_board(board, move, player_num):
    """
    Updates the game board with the player's move.
    INPUTS:
    board - a numpy array representing the game board
    move - the column where the player makes their move
    player_num - the number representing the player (1 or 2)
    RETURNS:
    None
    """
    if 0 in board[:, move]:
        update_row = -1
        for row in range(1, board.shape[0]):
            update_row = -1
            if board[row, move] > 0 and board[row-1, move] == 0:
                update_row = row-1
            elif row == board.shape[0]-1 and board[row, move] == 0:
                update_row = row
            if update_row >= 0:
                board[update_row, move] = player_num
                break
    else:
        err = 'Invalid move by player {}. Column {}'.format(player_num, move)
        raise Exception(err)

def game_completed(board, player_num):
    """
    Checks if the game is completed (i.e., if a player has won or if it's a draw).
    INPUTS:
    board - a numpy array representing the game board
    player_num - the number representing the player (1 or 2)
    RETURNS:
    True if the game is completed, False otherwise.
    """
    player_win_str = '{0}{0}{0}{0}'.format(player_num)
    to_str = lambda a: ''.join(a.astype(str))
    def check_horizontal(b):
        for row in b:
            if player_win_str in to_str(row):
                return True
        return False
    def check_vertical(b):
        return check_horizontal(b.T)
    def check_diagonal(b):
        for op in [None, np.fliplr]:
            op_board = op(b) if op else b
            root_diag = np.diagonal(op_board, offset=0).astype(int)
            if player_win_str in to_str(root_diag):
                return True
            for i in range(1, b.shape[1]-3):
                for offset in [i, -i]:
                    diag = np.diagonal(op_board, offset=offset)
                    diag = to_str(diag.astype(int))
                    if player_win_str in diag:
                        return True
        return False
    return (check_horizontal(board) or
            check_vertical(board) or
            check_diagonal(board))

def main(player1, player2, headless=False, num_games=10, seed=None):
    """
    Runs 100 games in headless mode and prints out the results.
    INPUTS:
    player1 - a string ['ai', 'random', 'human']
    player2 - a string ['ai', 'random', 'human']
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    def make_player(name, num):
        if name == 'ai':
            return AIPlayer(num)
        elif name == 'random':
            return RandomPlayer(num)
        elif name == 'human':
            return HumanPlayer(num)
    if headless:
        # initialize win counters for each player type
        player1_wins = 0
        player2_wins = 0
        draws = 0
        for _ in range(num_games):
            print("player1, ", player1)
            print("player2, ", player2)
            winner = play_headless_game(make_player(player1, 1), make_player(player2, 2))
            print("winner", winner)
            if winner == 1:
                player1_wins += 1
            elif winner == 2:
                player2_wins += 1
            else:
                draws += 1
        # print results based on player types
        print(f"Results after {num_games} headless games:")
        print(f"{player1} Player won: {player1_wins} games")
        print(f"{player2} Player won: {player2_wins} games")
        print(f"Draws: {draws}")
    else:
        # insert the existing GUI-based gameplay logic here or call a function that handles it
        Game(make_player(player1, 1), make_player(player2, 2), time)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('player1', choices=['ai', 'random', 'human'])
    parser.add_argument('player2', choices=['ai', 'random', 'human'])
    parser.add_argument('--headless', action='store_true', help='Run the game in headless mode')
    parser.add_argument('--num', type=int, default=10, help='Number of games to run in headless mode')
    parser.add_argument('--seed', type=int, help='Seed number for replicating the performance')
    args = parser.parse_args()
    main(args.player1, args.player2, args.headless, args.num, args.seed)
