
def press_event(x, y, game):
    """ Handles response to mouse press events.

    :param x: Mouse x-coordinate.
    :param y: Mouse y-coordinate.
    :param game: Tic-Tac-Toe Game object.
    """
    if game.winner is None:
        if game.turn is game.opponent:
            game.ai_place_marker()

        elif game.turn is game.player:
            square_index, square_center = game.clicked_square(x, y)
            if square_index:
                game.place_marker(square_index)

        game.clicked_square(x, y)

    else:
        game.clicked_button(x, y)


def release_event(x, y, game):
    """ Handles response to mouse release events.

    :param x: Mouse x-coordinate.
    :param y: Mouse y-coordinate.
    :param game: Tic-Tac-Toe Game object.
    """
    game.clicked_button(x, y)
