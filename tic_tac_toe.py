import numpy as np

from graphics import TicTacToeGrid, TextLabel, Marker, RectangleButton
from game_ai import minimax
from my_vector import Vector


# Game constants
STALE = 0
PLAYER_X = 1
PLAYER_O = 2

PLAYER_SYMBOLS = ('EMPTY', 'X', 'O')


class Board:
    """ Creates a 3x3 board for Tic-Tac-Toe.

    Every board starts as an empty (3,3) numpy.ndarray where the values are:
        - 0: Empty
        - 1: X
        - 2: O

    Important info:
        - 'self.turn' always starts as 1 (X).
        - 'self.winner' has 4 values:
            - None: Unfinished
            - 0: Stale
            - 1: X won
            - 2: O won
    """
    def __init__(self):
        self._spaces = np.zeros(shape=(3, 3), dtype=int)
        self._winner = None
        self.winner_symbol = None
        self.turn = PLAYER_X

    def __getitem__(self, key):
        return self._spaces[key]

    def __setitem__(self, key, value):
        self._spaces[key] = value
        self.check_win()

    @property
    def spaces(self):
        return self._spaces

    @spaces.setter
    def spaces(self, value):
        """ Setter makes sure to correct 'self.winner' if 'self.spaces' is set. """
        assert isinstance(value, np.ndarray) and value.shape == (3, 3), "spaces type must be a (3,3) numpy.ndarray"

        ones_tot = np.count_nonzero(value == PLAYER_X)
        twos_tot = np.count_nonzero(value == PLAYER_O)

        assert ones_tot == twos_tot or ones_tot == twos_tot + 1, "X's must be == O's or O's + 1"

        self._spaces = value
        self.check_win()

    @property
    def winner(self):
        return self._winner

    @winner.setter
    def winner(self, value):
        """ Setter makes sure to correct 'self.winner_symbol' if 'self.winner' is set. """
        self._winner = value
        if self.winner is PLAYER_X:
            self.winner_symbol = 'X'

        elif self.winner is PLAYER_O:
            self.winner_symbol = 'O'

        elif self.winner is STALE:
            self.winner_symbol = "STALE"

        else:
            self.winner_symbol = None

    def reset(self):
        """ Resets board to initial state. """
        self._spaces = np.zeros(shape=(3, 3), dtype=int)
        self.winner = None
        self.turn = PLAYER_X

    def get_rows(self):
        """ Gets all 'rows' that could contain 3 of the same marker in a row.

        :return: All possible "rows" of length 3.
        :rtype: list [numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray]
        """
        left_right_rows = self._spaces
        top_down_rows = self._spaces.transpose()
        diagonal_row = self._spaces.diagonal()
        flipped_diagonal_row = np.flip(self._spaces, axis=1).diagonal()

        return [*left_right_rows, *top_down_rows, diagonal_row, flipped_diagonal_row]

    def check_win(self):
        """ Checks all rows for winning condition and sets 'self.winner' accordingly.

        :return: None
        """
        if self.winner is not None:  # don't check win if already solved
            return

        rows = self.get_rows()
        for row in rows:
            if all(row == PLAYER_X):  # check if X won
                self.winner = PLAYER_X
                return

            if all(row == PLAYER_O):  # check if O won
                self.winner = PLAYER_O
                return

        # If there's no winner when board is full it's a stale
        if self._spaces.all():
            self.winner = STALE

    @staticmethod
    def get_rows_grid(board_grid):
        """ Gets all 'rows' that could contain 3 of the same marker in a row.

        :param board_grid: (3, 3) numpy.ndarray
        :return: All possible "rows" of length 3.
        :rtype: list [numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray] """
        left_right_rows = board_grid
        top_down_rows = board_grid.transpose()
        diagonal_row = board_grid.diagonal()
        flipped_diagonal_row = np.flip(board_grid, axis=1).diagonal()

        return [*left_right_rows, *top_down_rows, diagonal_row, flipped_diagonal_row]

    @staticmethod
    def check_win_grid(board_grid):
        """ Checks all rows for winning condition and sets 'self.winner' accordingly.

        :param board_grid: board_grid: (3, 3) numpy.ndarray
        :return: Winner of 'board_grid' setup.
        :rtype: None or int
        """
        winner = None

        rows = Board.get_rows_grid(board_grid)
        for row in rows:
            if all(row == PLAYER_X):  # check if X won
                winner = PLAYER_X
                return winner

            if all(row == PLAYER_O):  # check if O won
                winner = PLAYER_O
                return winner

        # If there's no winner when board is full it's a stale
        if board_grid.all():
            winner = STALE
            return winner

        # If not finished, return None
        return winner


class Game(Board):
    """ Creates a game of Tic-Tac-Toe against an optimally playing AI.

    This object sets up a game of Tic-Tac-Toe between the user and an unbeatable AI using
    a minimax algorithm to play optimally. Graphics and rendering is handled by custom
    classes and pyglet.

    :param player_symbol: "X" or "O"
    :param window_width: Program window width.
    :param window_height: Program window height.
    """
    PLAYERS = ('X', 'O')

    def __init__(self, player_symbol, window_width, window_height):
        assert player_symbol in self.PLAYERS, "Player must be 'X' or 'O'."
        self.player_symbol = player_symbol
        self.player = PLAYER_X if self.player_symbol is 'X' else PLAYER_O
        self.opponent = PLAYER_O if self.player_symbol is 'X' else PLAYER_X

        self.window_width = window_width
        self.window_height = window_height
        self.grid = TicTacToeGrid(self.window_width, self.window_height)

        self.buttons = {}
        self.button_params = {
            'rematch_button': {
                'pos': Vector(170, self.window_height-50),
                'text': "PLAY AGAIN",
                'action': self.rematch
            }
        }

        self.game_labels = {}
        self.game_label_params = {
            'winner_label': {
                'font_name': 'Arial',
                'font_size': 30,
                'pos': Vector(self.window_width - 200, self.window_height - 50),
            }
        }

        super().__init__()

    def end(self):
        """ Displays winner and "play again" button. """
        winner_text = "{} WON".format(self.winner_symbol) if self.winner_symbol is not "STALE" else "STALE"
        self.game_labels['winner_label'] = TextLabel(text=winner_text,
                                                     **self.game_label_params['winner_label'])

        self.buttons['rematch_button'] = RectangleButton(**self.button_params['rematch_button'])

    def end_turn(self):
        """ Swaps 'self.turn' to other player. """
        self.turn = PLAYER_O if self.turn is PLAYER_X else PLAYER_X

    def rematch(self):
        """ Resets board and clears makers and unnecessary labels. """
        self.reset()
        TextLabel.clear_all()
        RectangleButton.clear_all()

    def clicked_square(self, x, y):
        """ Get index of clicked square in Tic-Tac-Toe grid.

        :param x: Mouse x-coordinate
        :param y: Mouse y-coordinate
        :return: 'board' index of square clicked in Tic-Tac-Toe grid.
        :rtype: tuple (int, int)
        """
        square_index = self.grid.inside_square(x, y)
        return square_index

    def clicked_button(self, x, y):
        """ Checks game buttons if pressed/released and calls the correct action.

        :param x: Mouse x-coordinate
        :param y: Mouse y-coordinate
        """
        for key, button in self.buttons.items():
            if button.rectangle_object.inside_rectangle(x, y):

                if not button.pressed:
                    button.press()

                elif button.pressed:
                    button.release()
                    button.action()

    def place_marker(self, square_index):
        """

        :param square_index: Index of the selected Tic-Tac-Toe grid-square.
        :return: None if game is unfinished.
        """
        # Avoid placing marker if game is finished.
        if self.winner is not None:
            return

        # Values needed for drawing the markers.
        pos = self.grid.square_centers[square_index]  # center position of square in Tic-Tac-Toe grid
        pos = Vector(float(pos[0]), float(pos[1]))  # transform into Vector

        symbol = PLAYER_SYMBOLS[self.turn]  # get string symbol current player.

        # If square is empty, set marker on board and draw it.
        if not self.spaces[square_index]:
            self.spaces[square_index] = self.turn
            Marker(pos, symbol)

            # Swap turn and check if board is finished.
            self.end_turn()
            self.check_win()
            # If board is finished, end the game.
            if self.winner is not None:
                self.end()

    def ai_place_marker(self):
        """ Places marker using minimax algorithm. """
        # Avoid placing marker if game is finished.
        if self.winner is not None:
            return

        # Get optimal move and place marker accordingly.
        minimax_score, optimal_move = minimax(self.spaces, self.opponent, Board.check_win_grid)
        self.place_marker(optimal_move)
