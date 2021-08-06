import library.utilities
import client.fieldRender
import library.customObjects
import library.constants


class MouseInput:
    renderer: client.fieldRender.PlayingFieldRenderer
    player_object: library.customObjects.Player

    def __init__(
        self,
        renderer: client.fieldRender.PlayingFieldRenderer,
        player_object: library.customObjects.Player
    ):
        self.renderer = renderer
        self.player_object = player_object

    def player_mouse_input(self, event):
        pos = event.__dict__["pos"]
        # Convert from the window coordinates to shifted field
        # coordinates (to align center of the player rather than upper
        # side with the cursor)
        new_origin = self.renderer.field_origin
        new_origin = (new_origin[0], new_origin[1] + library.constants.PLAYER_SIZE[1]/2)
        pos = library.utilities.change_origin(pos, (0, 0), new_origin)
        y_desired = pos[1]

        # Clamp the position
        y_limit = library.constants.GAME_FIELD_SIZE[1] - library.constants.PLAYER_SIZE[1]
        y_desired = max(0, min(y_desired, y_limit))

        self.player_object.set_desired_move(0, y_desired - self.player_object.y_pos)
