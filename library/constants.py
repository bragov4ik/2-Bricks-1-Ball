from enum import Enum

############
# GAMEPLAY #
############
# Size of player rectangle
DEFAULT_RESOLUTION = (640, 480)

PLAYER_SIZE = (10, 60)
GAME_FIELD_SIZE = (500, 300)

BALL_RADIUS = 10
BALL_STARTING_POS = (250.0, 150.0)
BALL_STARTING_SPEED = (-1.0, 1.0)
TICK_RATE_LIMIT = 60

###################
# TECHNICAL STUFF #
###################

# Offset from behind (for visual appearance)
PLAYER_BACK_OFFSET = 5
# Offset from sides of the field (for visual appearance)
PLAYER_SIDE_OFFSET = 5
# Size of rendered rectangle representing the field
GAME_FIELD_RENDER_SIZE = (
    GAME_FIELD_SIZE[0] + PLAYER_BACK_OFFSET*2,
    GAME_FIELD_SIZE[1] + PLAYER_SIDE_OFFSET*2
)
# Offset from the top of the field to the score displayed above
SCORE_FONT_SIZE = 24
SCORE_FONT_COLOR = (255, 255, 255)
SCORE_OFFSET = 5
SCORE_DELIMITER = ':'

# Error allowed for pointInBox function (to account for computing
# imprecisions e.g. in matrix operations)
ERROR_MARGIN = 1e-10

class GameStatus(Enum):
    PAUSE = 0
    RUNNING = 1

WELCOME_MESSAGE = "Hello, I want to play!"