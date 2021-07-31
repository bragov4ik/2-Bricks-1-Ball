############
# GAMEPLAY #
############
# Size of player rectangle
PLAYER_SIZE = (10, 60)

DEFAULT_RESOLUTION = (640, 480)

#GAME_FIELD_SIZE = (500, 300)
GAME_FIELD_SIZE = (200, 100)

BALL_RADIUS = 10
BALL_STARTING_POS = (100.0, 35.0)
BALL_STARTING_SPEED = (-8.0, 3.0)
TICK_RATE_LIMIT = 240

#####################
# TECHNICAL DETAILS #
#####################

# Offset from behind (for visual appearance)
PLAYER_BACK_OFFSET = 5
# Offset from sides of the field (for visual appearance)
PLAYER_SIDE_OFFSET = 5
# Size of rendered rectangle representing the field
GAME_FIELD_RENDER_SIZE = (
    GAME_FIELD_SIZE[0] + PLAYER_BACK_OFFSET*2,
    GAME_FIELD_SIZE[1] + PLAYER_SIDE_OFFSET*2
)
# Error allowed for pointInBox function (to account for computing
# imprecisions e.g. in matrix operations)
ERROR_MARGIN = 1e-10
