from math import copysign
from typing import List
from enum import Enum
from functools import lru_cache

import library.utilities
import library.collisions
import library.constants
import library.customObjects


class GameState:
    ball: library.customObjects.Ball
    player_brick: library.customObjects.Player
    enemy_brick: library.customObjects.Player
    player_score: int
    enemy_score: int
    # Flags used to not check the same collision twice.
    # 4 sides : LEFT, UP, RIGHT, DOWN, player and enemy.  Needs to be
    # preserved between ticks
    collisions_resolved: List[bool]

    def __init__(self) -> None:
        self.ball = library.customObjects.Ball(
            x=library.constants.BALL_STARTING_POS[0],
            y=library.constants.BALL_STARTING_POS[1],
            scale=library.constants.BALL_RADIUS
        )
        self.ball.x_vel = library.constants.BALL_STARTING_SPEED[0]
        self.ball.y_vel = library.constants.BALL_STARTING_SPEED[1]
        self.player_brick = library.customObjects.Player(
            x_scale=library.constants.PLAYER_SIZE[0],
            y_scale=library.constants.PLAYER_SIZE[1]
        )
        self.enemy_brick = library.customObjects.Player(
            x=library.constants.GAME_FIELD_SIZE[0]-library.constants.PLAYER_SIZE[0],
            x_scale=library.constants.PLAYER_SIZE[0],
            y_scale=library.constants.PLAYER_SIZE[1]
        )
        self.player_score = 0
        self.enemy_score = 0
        self.collisions_resolved = [False]*6

    def tick_state(self, t):
        # Players' moves
        for player in (self.player_brick, self.enemy_brick):
            self.players_physics(player)
        self.ball_physics(t)

    @lru_cache(maxsize=64)
    def generate_sides(r):
        """
        Generates a tuple of segments representing field sides in the
        order LEFT, UP, RIGHT, DOWN
        """
        return (
            (
                (r, r),
                (r, r+library.constants.GAME_FIELD_SIZE[1])
            ),
            (
                (r, r),
                (-r+library.constants.GAME_FIELD_SIZE[0], r)
            ),
            (
                (-r+library.constants.GAME_FIELD_SIZE[0], r),
                (
                    -r+library.constants.GAME_FIELD_SIZE[0],
                    -r+library.constants.GAME_FIELD_SIZE[1]
                )
            ),
            (
                (r, -r+library.constants.GAME_FIELD_SIZE[1]),
                (
                    -r+library.constants.GAME_FIELD_SIZE[0],
                    -r+library.constants.GAME_FIELD_SIZE[1]
                )
            )
        )


    def ball_physics(self, t):
        """
        Handles the ball's physics (moving forward, bouncing off the
        walls and bricks) + checks if it touched side walls (win 
        condition)
        """
        cur_move = (
            self.ball.x_vel*t*1e-1,
            self.ball.y_vel*t*1e-1
        )
        cur_start = (
            self.ball.x_pos,
            self.ball.y_pos
        )
        cur_end = (
            cur_start[0] + cur_move[0],
            cur_start[1] + cur_move[1]
        )

        # LEFT, UP, RIGHT, DOWN. Cached method, no need to worry
        # about performance if the size is unchanged
        sides = GameState.generate_sides(self.ball.x_scale)
        
        collision_list: List[library.customObjects.Collision] = None
        # Indexes in collisionsResolved list of found collisions
        collisions_ids: List[int] = []
        while (
            collision_list == None
            or (collision_list
                and library.utilities.distance(cur_start, cur_end) != 0)    # Not magnitude of move!!!
        ):
            # Find all possible collisions
            collision_list = []
            collisions_ids = []
            # Checking sides
            for i in range(len(sides)):
                if self.collisions_resolved[i]:
                    # Resolution of the collision skips only one
                    # iteration
                    self.collisions_resolved[i] = False
                    continue
                side = sides[i]
                new_collisions = library.collisions.collision_vector_segment(
                    cur_start, cur_end, side[0], side[1]
                )
                collision_list += new_collisions
                if new_collisions:
                    collisions_ids += [i]*len(new_collisions)
            # Collisions with player1
            if self.collisions_resolved[4]:
                self.collisions_resolved[4] = False
            else:
                new_collisions = library.collisions.collision_ball_brick(
                    self.ball,
                    self.player_brick,
                    cur_start,
                    cur_move
                )
                collision_list += new_collisions
                if new_collisions:
                    collisions_ids += [4]*len(new_collisions)
            # Collisions with player2
            if self.collisions_resolved[5]:
                self.collisions_resolved[5] = False
            else:
                new_collisions = library.collisions.collision_ball_brick(
                    self.ball,
                    self.enemy_brick,
                    cur_start,
                    cur_move
                )
                collision_list += new_collisions
                if new_collisions:
                    collisions_ids += [5]*len(new_collisions)
            if len(collision_list) == 0:
                continue

            # Extract the one closest to the start
            closest = library.collisions.get_closest_collision(
                cur_start,
                collision_list
            )
            if closest == None:
                # Must not happen as length check for 0 is not passed
                raise IndexError("No collisions to handle!")
            closest_collision = closest[0]
            closest_collision_id = collisions_ids[closest[1]]

            # If the collision happens with the walls, update the score
            # and reset the game
            if closest_collision_id in (0, 2):
                winner: self.Players
                if closest_collision_id == 0:
                    # LEFT wall
                    winner = self.Players.PLAYER_2
                elif closest_collision_id == 2:
                    # RIGHT wall
                    winner = self.Players.PLAYER_1
                self.handle_goal(winner)
                return

            # Resolve the closest collision
            cur_move = library.collisions.resolve_collision(
                cur_start,
                cur_move,
                closest_collision
            )
            cur_start = closest_collision.position
            cur_end = (
                cur_start[0] + cur_move[0],
                cur_start[1] + cur_move[1]
            )
            (self.ball.x_vel, self.ball.y_vel) = library.utilities.mirror_vector_2d(
                (self.ball.x_vel, self.ball.y_vel),
                closest_collision.normal
            )
            self.collisions_resolved[closest_collision_id] = True
        # No more collisions here
        cur_end = (
            cur_start[0] + cur_move[0],
            cur_start[1] + cur_move[1]
        )
        self.ball.x_pos = cur_end[0]
        self.ball.y_pos = cur_end[1]


    def players_physics(
        self,
        player: library.customObjects.Player
    ):
        """
        Move the given player in such a way that it won't collide into
        the ball.  Instead it stops right before it (with a small gap).
        Motion is done according to the player's desiredMove field.
        """
        # Convert the problem of moving brick into a ball to
        # moving ball into a brick (we see brick as the point of
        # reference), since we already have such collision checking
        # implemented.

        # The ball therefore moves in opposite direction (as
        # point of reference has changed)
        ball_move = (
            -player.desired_move[0],
            -player.desired_move[1]
        )
        ball_pos = (self.ball.x_pos, self.ball.y_pos)

        # Get the collision point
        returned_val = library.collisions.get_closest_collision(
            ball_pos,
            library.collisions.collision_ball_brick(
                self.ball, player, ball_pos, ball_move
            )
        )
        if returned_val == None:
            # No collisions with the ball, can move freely
            player.move_by(*(player.desired_move))
            player.set_desired_move(0.0, 0.0)
        else:
            # Collision found! Handle:
            (collision, _) = returned_val

            # Player's move would be the vector starting from the
            # collision point to the ball

            # x component is always static, so let's leave it
            y_player_move = ball_pos[1] - collision.position[1]
            # To prevent repeated colliding with the ball (since
            # it causes the ball to bounce inside the brick), add
            # a little gap.
            y_player_move = (y_player_move
                            - copysign(
                                library.constants.ERROR_MARGIN,
                                y_player_move
                            ))
            new_player_move = (
                0,
                y_player_move
            )
            player.move_by(new_player_move[0], new_player_move[1])
            player.set_desired_move(0.0, 0.0)
        

    def reset_entities(self):
        self.ball.x_pos = library.constants.BALL_STARTING_POS[0]
        self.ball.y_pos = library.constants.BALL_STARTING_POS[1]
        self.ball.x_vel = library.constants.BALL_STARTING_SPEED[0]
        self.ball.y_vel = library.constants.BALL_STARTING_SPEED[1]
        self.player_brick.x_pos = 0.0
        self.player_brick.y_pos = 0.0
        self.player_brick.desired_move[0] = 0.0
        self.player_brick.desired_move[1] = 0.0
        self.enemy_brick.x_pos = (library.constants.GAME_FIELD_SIZE[0]
                                - library.constants.PLAYER_SIZE[0])
        self.enemy_brick.y_pos = 0.0
        self.enemy_brick.desired_move[0] = 0.0
        self.enemy_brick.desired_move[1] = 0.0
        self.collisions_resolved = [False]*6

    
    class Players(Enum):
        PLAYER_1 = 1
        PLAYER_2 = 2


    def handle_goal(
        self,
        player: Players
    ):
        if player == self.Players.PLAYER_1:
            self.player_score += 1
        elif player == self.Players.PLAYER_2:
            self.enemy_score += 1
        print("Score {}:{}".format(self.player_score, self.enemy_score))
        self.reset_entities()
        