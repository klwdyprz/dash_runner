import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 400
GROUND_Y = 320

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
RED = (220, 60, 60)
BLUE = (60, 120, 220)
GRAY = (200, 200, 200)
ORANGE = (230, 150, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dash Runner")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 28)
big_font = pygame.font.SysFont("consolas", 48)

class Player:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.duck_height = 16
        self.x = 80
        self.y = GROUND_Y - self.height
        self.vel_y = 0
        self.gravity = 0.9
        self.jump_power = -15
        self.on_ground = True
        self.jumps_left = 2      
        self.max_jumps = 2
        self.ducking = False

    def jump(self):
        if self.jumps_left > 0:
            self.vel_y = self.jump_power
            self.jumps_left -= 1
            self.on_ground = False

    def start_duck(self):
        if self.on_ground:
            self.ducking = True

    def stop_duck(self):
        self.ducking = False

    def update(self):
        current_height = self.duck_height if self.ducking else self.height
        ground_top = GROUND_Y - current_height

        self.vel_y += self.gravity
        self.y += self.vel_y

        if self.y >= ground_top:
            self.y = ground_top
            self.vel_y = 0
            self.on_ground = True
            self.jumps_left = self.max_jumps
        else:
            self.on_ground = False

    def draw(self):
        current_height = self.duck_height if self.ducking else self.height
        color = ORANGE if self.ducking else BLUE
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, current_height))

    def get_rect(self):
        current_height = self.duck_height if self.ducking else self.height
        return pygame.Rect(self.x, self.y, self.width, current_height)

class Obstacle:
    """Ground obstacle - jump over it."""
    def __init__(self):
        self.width = random.randint(20, 35)
        self.height = random.randint(30, 60)
        self.x = WIDTH
        self.y = GROUND_Y - self.height
        self.kind = "ground"

    def update(self, speed):
        self.x -= speed

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def off_screen(self):
        return self.x + self.width < 0


class FlyingObstacle:
    """Flying obstacle - duck under it."""
    def __init__(self):
        self.width = 34
        self.height = 18
        self.x = WIDTH
        self.y = GROUND_Y - 40
        self.kind = "flying"

    def update(self, speed):
        self.x -= speed

    def draw(self):
        pygame.draw.rect(screen, (150, 60, 200), (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def off_screen(self):
        return self.x + self.width < 0

def reset_game():
    global player, obstacles, score, speed, spawn_timer, game_over
    player = Player()
    obstacles = []
    score = 0
    speed = 6
    spawn_timer = 0
    game_over = False


def spawn_obstacle():
    if random.random() < 0.3:
        obstacles.append(FlyingObstacle())
    else:
        obstacles.append(Obstacle())


def draw_ground():
    pygame.draw.line(screen, BLACK, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)


def draw_text_center(text, font_obj, color, y):
    render = font_obj.render(text, True, color)
    rect = render.get_rect(center=(WIDTH // 2, y))
    screen.blit(render, rect)

reset_game()
started = False

while True:
    clock.tick(60)
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not started:
                    started = True
                elif game_over:
                    reset_game()
                    started = True
                else:
                    player.jump()

            if event.key == pygame.K_DOWN and started and not game_over:
                player.start_duck()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player.stop_duck()

    if not started:
        draw_text_center("DASH RUNNER", big_font, BLACK, 120)
        draw_text_center("Press SPACE to start", font, GRAY, 190)
        draw_text_center("SPACE = jump (x2)   DOWN = duck", font, GRAY, 230)
        draw_ground()
        pygame.display.flip()
        continue

    if not game_over:
        speed += 0.002

        player.update()

        spawn_timer -= 1
        if spawn_timer <= 0:
            spawn_obstacle()
            spawn_timer = random.randint(60, 110)

        for obs in obstacles[:]:
            obs.update(speed)
            if obs.off_screen():
                obstacles.remove(obs)
                score += 1

        for obs in obstacles:
            if player.get_rect().colliderect(obs.get_rect()):
                game_over = True

    draw_ground()
    player.draw()
    for obs in obstacles:
        obs.draw()

    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (20, 20))

    if game_over:
        draw_text_center("GAME OVER", big_font, RED, 150)
        draw_text_center("Press SPACE to restart", font, GRAY, 200)

    pygame.display.flip()