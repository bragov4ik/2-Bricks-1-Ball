import utilities
import fieldRender
import customObjects
import constants


class MouseInput:
    renderer: fieldRender.PlayingFieldRenderer
    playerObject: customObjects.Player

    def __init__(
        self,
        renderer: fieldRender.PlayingFieldRenderer,
        playerObject: customObjects.Player
    ):
        self.renderer = renderer
        self.playerObject = playerObject

    def playerMouseInput(self, event):
        pos = event.__dict__["pos"]
        # Convert from the window coordinates to shifted field
        # coordinates (to align center of the player rather than upper
        # side with the cursor)
        newOrigin = self.renderer.fieldOrigin
        newOrigin = (newOrigin[0], newOrigin[1] + constants.PLAYER_SIZE[1]/2)
        pos = utilities.changeOrigin(pos, (0, 0), newOrigin)
        yDesired = pos[1]

        # Clamp the position
        yLimit = constants.GAME_FIELD_SIZE[1] - constants.PLAYER_SIZE[1]
        yDesired = max(0, min(yDesired, yLimit))

        self.playerObject.setDesiredMove(0, yDesired - self.playerObject.yPos)
