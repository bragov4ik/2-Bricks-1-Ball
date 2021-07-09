import pygame
import utilities

class Game:
    quitGame = False
    colorBackgr = (255, 128, 0)

    circleLoc = (250, 250)
    circleR = 100
    colorCirc = (200, 128, 200)

    lineUpdated = True
    lineStart = (100, 100)
    lineEnd = (400, 200)
    colorLine = (200, 200, 200)

    collisions = []
    colorCollision = (240, 240, 230)

    movementKeysPressed1 = set()
    movementKeysPressed2 = set()


    def init(self):
        pygame.init()
        self.window = pygame.display.set_mode((640, 480), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

    def processInput(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.quitGame = True
        elif event.type == pygame.KEYDOWN:
            key = event.__dict__["key"]
            if key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                self.movementKeysPressed1.add(key)
            if key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                self.movementKeysPressed2.add(key)
        elif event.type == pygame.KEYUP:
            key = event.__dict__["key"]
            if key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                self.movementKeysPressed1.remove(key)
            if key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                self.movementKeysPressed2.remove(key)
    
    def updateState(self):
        self.clock.tick(60)
        if len(self.movementKeysPressed1) != 0:
            input = next(iter(self.movementKeysPressed1))
            move = (0, 0)
            if input == pygame.K_UP:
                move = (0, -1)
            elif input == pygame.K_DOWN:
                move = (0, 1)
            elif input == pygame.K_LEFT:
                move = (-1, 0)
            elif input == pygame.K_RIGHT:
                move = (1, 0)
            self.lineStart = tuple(map(sum, zip(self.lineStart, move)))
            print(self.lineStart)
            self.lineUpdated = True

        if len(self.movementKeysPressed2) != 0:
            input = next(iter(self.movementKeysPressed2))
            move = (0, 0)
            if input == pygame.K_w:
                move = (0, -1)
            elif input == pygame.K_s:
                move = (0, 1)
            elif input == pygame.K_a:
                move = (-1, 0)
            elif input == pygame.K_d:
                move = (1, 0)
            self.lineEnd = tuple(map(sum, zip(self.lineEnd, move)))
            self.lineUpdated = True
            

        if self.lineUpdated:
            self.collisions = utilities.collisionLineCircle(self.lineStart, self.lineEnd, self.circleLoc, self.circleR)
            print(self.collisions)
            self.lineUpdated = False

    
    def render(self):
        # Draw background

        pygame.draw.rect(
            self.window, 
            self.colorBackgr, 
            (0, 0) + pygame.display.get_window_size()
        )

        # Draw circle
        pygame.draw.circle(
            self.window,
            self.colorCirc,
            self.circleLoc,
            self.circleR
        )

        # Draw the line
        pygame.draw.line(
            self.window,
            self.colorLine,
            self.lineStart,
            self.lineEnd,
            2
        )

        # Draw collisions
        for col in self.collisions:
            pygame.draw.circle(
                self.window,
                self.colorCollision,
                col,
                3
            )

        pygame.display.update()

    def run(self):
        self.init()
        while not self.quitGame:
            self.processInput()
            self.updateState()
            self.render()
        pygame.quit()
        

game = Game()
game.run()