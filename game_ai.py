import numpy as np


def minimax(board, player, check_win, **kwargs):
    """ Minimax algorithm to get the optimal Tic-Tac-Toe move on any board setup.

    This recursive function uses the minimax algorithm to look over each possible move
    and minimize the possible loss for a worst case scenario. For a deeper understanding
    and examples see: 'Wikipedia <https://en.wikipedia.org/wiki/Minimax>'_.

    :param board: 3x3 numpy ndarray where 0 is empty, 1 is X, 2 is O.
    :param player: Determines player: 1 if X, 2 if O.
    :param check_win: Function that takes a 'board' and returns: 0 if stale, 1 if X won, 2 if O won.
    :param kwargs: Used in the recursion to pass the last move made.
    :return: 'score' and index of optimal Tic-Tac-Toe 'move' given a 3x3 board.
    :rtype: float, tuple (int, int)
    """

    EMPTY = 0
    STALE = 0
    WIN = 1
    PLAYER_X = 1
    PLAYER_O = 2

    assert isinstance(board, np.ndarray) and board.shape == (3,3), 'board must be a (3,3) numpy.ndarray'
    assert player is PLAYER_X or PLAYER_O, 'player must be an int 1 (X) or 2 (O).'

    # Get the constant integer value of the opponent.
    opponent = PLAYER_X if player == PLAYER_O else PLAYER_O

    # Return correct reward if there's a winner.
    winner = check_win(board)
    if winner == player:
        board[kwargs['last_move']] = EMPTY
        return WIN

    elif winner == opponent:
        board[kwargs['last_move']] = EMPTY
        return -WIN

    move = -1
    score = float('-inf')

    # Get indices of available moves.
    available_moves = np.where(board == EMPTY)
    am_indices = list(zip(*available_moves))

    # Try each move
    for move_index in am_indices:
        # Make copy of current board grid.
        board_copy = board

        # Make move on copy
        board_copy[move_index] = player

        move_score = -minimax(board_copy, opponent, check_win, last_move=move_index)

        if move_score > score:
            score = move_score
            move = move_index

    if move == -1:
        board[kwargs['last_move']] = EMPTY
        return STALE

    # If the keyword-argument is not found, it must be the last recursion and
    # should therefore return the best move and its score.
    try:
        board[kwargs['last_move']] = EMPTY
    except KeyError:
        return score, move

    return score