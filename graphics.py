from my_vector import Vector  # custom 2d vector class

import numpy as np
import math
from pyglet.text import Label


class GraphicsObject:
    graphics_objects = []


class Rectangle(GraphicsObject):
    """ Simple rectangle object compatible with pyglet.

    :param width: Rectangle width.
    :param height: Rectangle height.
    :param pos: Rectangle center position as Vector.
    :param rotation: Rectangle rotation in radians.
    :param hidden: Does not get drawn in batch if True.
    """
    # Constants
    VTOT = 4  # total vertices

    def __init__(self, width, height, pos=Vector(0,0), rotation=0, hidden=False):
        assert isinstance(pos, Vector), '\'pos\' must be a Vector object.'

        self.width = width
        self.height = height
        self.pos = pos
        self.rotation = rotation
        self.hidden = hidden

        # Setup all vertices as Vectors
        self.v0 = []  # bottom left
        self.v1 = []  # bottom right
        self.v2 = []  # top right
        self.v3 = []  # top left
        self.set_vertices()

        # Add Rectangle object to graphics_objects in parent class.
        super().graphics_objects.append(self)

    def set_vertices(self):
        """ Sets vertices to correct values based on instance attributes. """
        if self.rotation == 0:
            self.v0, self.v1, self.v2, self.v3 = self.non_rotated_vertices()
        else:
            self.v0, self.v1, self.v2, self.v3 = self.rotated_vertices()

    def non_rotated_vertices(self):
        """ Get vertices when the rectangle's rotation is 0.

        :return: Vertices as lists containing (x, y) coordinates.
        """
        v0 = [self.pos.x - self.width / 2, self.pos.y - self.height / 2]
        v1 = [self.pos.x + self.width / 2, self.pos.y - self.height / 2]
        v2 = [self.pos.x + self.width / 2, self.pos.y + self.height / 2]
        v3 = [self.pos.x - self.width / 2, self.pos.y + self.height / 2]
        return v0, v1, v2, v3

    def rotated_vertices(self):
        """ Get coordinates for vertices based on the rectangles rotation.

        :return: Vertices as lists containing (x, y) coordinates.
        :rtype: list
        """
        rotated_vertices = []
        for v in self.non_rotated_vertices():
            x, y = v[0], v[1]
            x_rotated = self.pos.x + (x-self.pos.x)*math.cos(self.rotation) - (y-self.pos.y)*math.sin(self.rotation)
            y_rotated = self.pos.y + (x-self.pos.x)*math.sin(self.rotation) + (y-self.pos.y)*math.cos(self.rotation)
            rotated_vertices.append([x_rotated, y_rotated])
        return rotated_vertices

    def vertices_tuple(self):
        """ Returns vertices in tuple format compatible with pyglet batches. """
        vtuple = (*self.v0, *self.v1, *self.v2, *self.v3)
        return vtuple

    @staticmethod
    def center(width, height):
        """ Returns center of a rectangle.

        :param width: Width of rectangle
        :param height: Height of rectangle
        :return: x and y value of rectangle center
        :rtype: float, float
        """
        return width/2, height/2

    def batch_params(self):
        """ Returns all parameters needed for a Pyglet batch. """
        return self.VTOT, self.vertices_tuple()

    def inside_rectangle(self, x, y):
        """ Returns True if (x, y) is inside borders of rectangle.

        :param x: Mouse x-coordinate.
        :param y: Mouse y-coordinate.
        :return: True if x and y is inside borders of rectangle instance.
        """
        if (self.pos.x - self.width < x < self.pos.x + self.width and
                self.pos.y - self.height < y < self.pos.y + self.height):
            return True


class GridLine(Rectangle):
    """ Template for gridline part of Tic-Tac-Toe grid.

    :param horizontal: Makes horizontal gridline if True.
    """
    def __init__(self, width=35, height=600, horizontal=False):
        if horizontal:
            width, height = height, width

        super().__init__(width, height)


class TicTacToeGrid:
    """ Creates 4 GridLine objects in a 2d grid-like structure for Tic-Tac-Toe.

    :param window_width: Width of window to render in
    :param window_height: Height of window to render in
    :param spacing: Space between center and middle of each GridLine
    """

    GRID_SHAPE = (3, 3)

    def __init__(self, window_width, window_height, spacing=100):
        self.window_width = window_width
        self.window_height = window_height
        self.spacing = spacing
        self.center = Rectangle.center(self.window_width, self.window_height)

        # Setup grid lines and their positions with respect to the window size
        self.lines = {
            'left_vertical_line': GridLine(),
            'right_vertical_line': GridLine(),
            'top_horizontal_line': GridLine(horizontal=True),
            'bot_horizontal_line': GridLine(horizontal=True)
        }
        self.setup_lines()

        self.grid_width = self.lines['top_horizontal_line'].width
        self.grid_height = self.lines['left_vertical_line'].height

        # Center coordinates of each square from top left to bottom right.
        self.square_centers = self.get_square_centers()
        self.square_width = 2 * self.spacing - self.lines['left_vertical_line'].width
        self.square_width_half = self.square_width / 2

    def setup_lines(self):
        """ Calls methods needed for setup of grid. """
        self.center_lines()
        self.space_lines()

    def center_lines(self):
        """ Moves all lines to center of window. """
        window_center = Rectangle.center(self.window_width, self.window_height)
        for line in self.lines.values():
            line.pos = Vector(*window_center)
            line.set_vertices()

    def space_lines(self):
        """ Add spacing between lines and center. """
        self.lines['left_vertical_line'].pos.x -= self.spacing
        self.lines['right_vertical_line'].pos.x += self.spacing
        self.lines['top_horizontal_line'].pos.y += self.spacing
        self.lines['bot_horizontal_line'].pos.y -= self.spacing

        # Call set_vertices manually since pos.setter is not used.
        for line in self.lines.values():
            line.set_vertices()

    def get_square_centers(self):
        """ Returns coordinates of the 9 grid square centers.

        :return: (x, y) coordinate pairs
        :rtype: numpy.ndarray
        """
        x_values = np.arange(-2, 4, 2) * np.ones(self.GRID_SHAPE)
        y_values = np.arange(2, -4, -2).reshape((3, 1)) * np.ones(self.GRID_SHAPE)
        x_values *= self.spacing
        x_values += self.center[0] # add x-coordinate for grid center
        y_values *= self.spacing
        y_values += self.center[1] # add y-coordinate for grid center
        return np.dstack((x_values, y_values))

    def inside_square(self, x, y):
        """ Returns index of grid square mouse is inside and the coordinates of its center.

        :param x: Mouse x-coordinate.
        :param y: Mouse y-coordinate.
        :return: Index of grid square mouse is inside and coordinates of its center.
        :rtype: tuple

        """
        square_centers = self.get_square_centers()
        for i, row in enumerate(square_centers):
            for j, (square_x, square_y) in enumerate(row):

                if (square_x - self.square_width_half < x < square_x + self.square_width_half and
                        square_y - self.square_width_half < y < square_y + self.square_width_half):

                    return (i, j), (float(square_x), float(square_y))

        return None, None


class TextLabel:
    """ Object to easily handle and draw text on pyglet window.

    :param pos: Vector position of label on pyglet window.
    :param text: Label text.
    :param font_size: Font size.
    :param font_name: Font name.
    """

    text_labels = []

    # pyglet Label parameters.
    ANCHOR_X, ANCHOR_Y = 'center', 'center'

    def __init__(self, pos, text, font_size=40, font_name='Arial'):
        assert isinstance(pos, Vector), "pos must be a Vector object."
        assert isinstance(text, str), "text must be a string"
        self.pos = pos
        self.text = text
        self.font_size = font_size
        self.font_name = font_name

        self.text_labels.append(self)

    def batched_drawing(self, batch):
        """ Draws label to passed pyglet batch.

        :param batch: pyglet batch object.
        """
        Label(self.text, font_name=self.font_name, font_size=self.font_size,
              x=self.pos.x, y=self.pos.y, anchor_x=self.ANCHOR_X, anchor_y=self.ANCHOR_Y,
              batch=batch)

    @classmethod
    def clear_all(cls):
        """ Deletes all TextLabel objects. """
        del cls.text_labels[:]


class Marker(TextLabel):
    """ Marker object for Tic-Tac-Toe. """
    markers = []

    def __init__(self, pos, text, font_size=120):
        super().__init__(pos, text, font_size=font_size)

        self.markers.append(self)

    @classmethod
    def clear_all_markers(cls):
        """ Deletes all Marker objects. """
        # Clear all markers from superclass list 'text_labels'.
        cls.text_labels[:] = [tl for tl in cls.text_labels if not isinstance(tl, Marker)]
        del cls.markers[:]


class Button:
    """ Simple button object for use with pyglet.

    :param pos: Vector position of button.
    :param action: Function for button response.
    """
    buttons = []

    def __init__(self, pos, action):
        assert isinstance(pos, Vector), "pos must be a Vector object."
        self.pos = pos
        self.action = action
        self.pressed = False

    def press(self):
        self.pressed = True

    def release(self):
        self.pressed = False

    @classmethod
    def clear_all(cls):
        """ Delete all button objects. """
        del cls.buttons[:]


class RectangleButton(Button):
    """ Button object for drawing a rectangular button.

    This version has the Rectangle object hidden meaning that it's only use is for
    interacting with the mouse.

    :param pos: Vector position of button.
    :param action: Function for button response.
    :param width: Width of rectangle.
    :param height: Height of rectangle.
    :param text: Button text.
    :param font_size: Font size.
    :param font_name: Font name.
    """
    ANCHOR_X, ANCHOR_Y = 'center', 'center'

    def __init__(self, pos, action, width=100, height=30, text="", font_size=30, font_name='Arial'):
        super().__init__(pos, action)
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.font_name = font_name
        # self.hidden = False
        self.label_object = None
        self.rectangle_object = None

        self.buttons.append(self)

    def batched_drawing(self, batch):
        """ Currently handles both batched drawing of pyglet label and the creation of the Rectangle. """
        self.label_object = Label(self.text, font_name=self.font_name, font_size=self.font_size,
                                  x=self.pos.x, y=self.pos.y, anchor_x=self.ANCHOR_X, anchor_y=self.ANCHOR_Y,
                                  batch=batch)

        # Rectangle objects are added to the batch "automatically" since it's a subclass of GraphicsObject.
        self.rectangle_object = Rectangle(self.width, self.height, pos=self.pos, hidden=True)




