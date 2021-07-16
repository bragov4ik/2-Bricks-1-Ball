# Size of player rectangle
PLAYER_SIZE = (10, 60)
# Offset from behind (for visual appearance)
PLAYER_BACK_OFFSET = 5
# Offset from sides of the field
PLAYER_SIDE_OFFSET = 5

DEFAULT_RESOLUTION = (640, 480)

GAME_FIELD_SIZE = (500, 300)
GAME_FIELD_RENDER_SIZE = (
        500 + PLAYER_BACK_OFFSET*2,
        300 + PLAYER_SIDE_OFFSET*2
)
BALL_RADIUS = 10

TICK_RATE_LIMIT = 256
