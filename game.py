import pyglet
from pyglet.window import mouse

from tic_tac_toe import Game
from graphics import GraphicsObject, TextLabel, Button
from events import press_event, release_event


# Window constants
WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280

# Drawing constants
MODE = 'GL_QUADS'
BATCH_GROUP = None
DRAW_FORMAT = 'v2f'


def setup_window():
    new_window = pyglet.window.Window(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    return new_window


def create_batch():
    batch = pyglet.graphics.Batch()

    # Put polygons in batch.
    for graphics_object in GraphicsObject.graphics_objects:
        if not graphics_object.hidden:
            vtot, vertices = graphics_object.batch_params()
            batch_parameters = (vtot, getattr(pyglet.graphics, MODE), BATCH_GROUP, (DRAW_FORMAT, vertices))
            batch.add(*batch_parameters)

    # Put all game markers (pyglet labels) in batch.
    for text_label in TextLabel.text_labels:
        text_label.batched_drawing(batch)

    # Put all buttons in batch.
    for button in Button.buttons:
        button.batched_drawing(batch)

    return batch


if __name__ == "__main__":
    new_game = Game('X', WINDOW_WIDTH, WINDOW_HEIGHT)

    window = setup_window()

    @window.event
    def on_draw():
        window.clear()
        batch = create_batch()
        batch.draw()


    @window.event
    def on_mouse_press(x, y, button, modifiers):
        if button == mouse.LEFT:
            press_event(x, y, new_game)

    @window.event
    def on_mouse_release(x, y, button, modifiers):
        if button == mouse.LEFT:
            release_event(x, y, new_game)

    pyglet.app.run()
