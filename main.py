
import pygame, sys
import asyncio

WIDTH, HEIGHT = 800, 600
FLOOR_Y = 500
GRAVITY = 1
JUMP_POWER = 18
WALK_SPEED = 0.5
BOX_SPEED = 3.0
FPS = 60

class Stickman:
    def __init__(self, start_x, start_y):
        # Load images
        self.images_run = [
            pygame.image.load("images/run1.png").convert_alpha(),
            pygame.image.load("images/run2.png").convert_alpha(),
            pygame.image.load("images/run3.png").convert_alpha(),
            pygame.image.load("images/run4.png").convert_alpha(),
        ]
        self.image_jump = pygame.image.load("images/run5.png").convert_alpha()
        self.image = self.images_run[0]

        # Use float positions for smooth motion
        self.pos_x = start_x
        self.pos_y = start_y
        self.rect = self.image.get_rect(center=(self.pos_x, self.pos_y))

        self.is_jumping = False
        self.y_velocity = 0
        self.anim_frame = 0
        self.anim_timer = 0.0  # seconds

    def start_jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.y_velocity = JUMP_POWER
            self.image = self.image_jump

    def update_motion(self, dt):
        # Move slowly right (like your PGZero version)
        self.pos_x += WALK_SPEED
        if self.pos_x > WIDTH - 100:
            self.pos_x = WIDTH - 100

        # Jumping & gravity (same logic as your PGZero code)
        if self.is_jumping:
            self.y_velocity -= GRAVITY
            self.pos_y -= self.y_velocity

            if self.pos_y >= FLOOR_Y:
                self.pos_y = FLOOR_Y
                self.is_jumping = False
                self.y_velocity = 0
                # reset to walking frame 0
                self.anim_timer = 0
                self.anim_frame = 0
                self.image = self.images_run[self.anim_frame]
        else:
            # Walking animation only when on ground
            self.anim_timer += dt
            if self.anim_timer >= 1.0 / 12.0:  # 12 frames/sec
                self.anim_timer = 0.0
                self.anim_frame = (self.anim_frame + 1) % len(self.images_run)
                self.image = self.images_run[self.anim_frame]

        # Update rect from float position
        self.rect.center = (int(self.pos_x), int(self.pos_y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Box:
    def __init__(self, start_x, start_y):
        self.image = pygame.image.load("images/box1.png").convert_alpha()
        self.pos_x = start_x
        self.pos_y = start_y
        self.rect = self.image.get_rect(center=(self.pos_x, self.pos_y))

    def update_motion(self, dt):
        # Move box left, return True when it wraps (for scoring)
        wrapped = False
        self.pos_x -= BOX_SPEED
        if self.pos_x < -50:
            self.pos_x = WIDTH + 50
            wrapped = True
        self.rect.center = (int(self.pos_x), int(self.pos_y))
        return wrapped

    def draw(self, surface):
        surface.blit(self.image, self.rect)


async def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Stickman Jump - Innovus Innovation Center")

    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont(None, 32)
    font_large = pygame.font.SysFont(None, 64)

    score = 0
    state = "splash"  # "splash", "playing", "game_over"

    stickman_guy = Stickman(100, FLOOR_Y)
    obstacle_box = Box(700, FLOOR_Y)

    def reset_game():
        nonlocal score, stickman_guy, obstacle_box, state
        score = 0
        stickman_guy = Stickman(100, FLOOR_Y)
        obstacle_box = Box(700, FLOOR_Y)
        state = "splash"

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # seconds since last frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Splash screen: click/tap or any key to start
            if state == "splash":
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    state = "playing"

            # Main game: Space OR click/tap = jump
            elif state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        stickman_guy.start_jump()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    stickman_guy.start_jump()

            # Game over: click/tap or any key to reset
            elif state == "game_over":
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    reset_game()

        # --- UPDATE ---
        if state == "playing":
            stickman_guy.update_motion(dt)
            if obstacle_box.update_motion(dt):
                score += 1

            # Collision detection near the ground (similar to your PGZero logic)
            if stickman_guy.rect.colliderect(obstacle_box.rect):
                if (stickman_guy.rect.bottom > obstacle_box.rect.top + 5 and
                        stickman_guy.pos_y >= FLOOR_Y - 20):
                    state = "game_over"

        # --- DRAW ---
        screen.fill((50, 150, 200))

        # Draw the floor
        pygame.draw.rect(
            screen,
            (0, 150, 0),
            (0, FLOOR_Y + 20, WIDTH, HEIGHT - FLOOR_Y)
        )

        if state == "splash":
            # Ultra-compact intro text
            title = font_large.render("Innovus Innovation Center", True, (255, 255, 255))
            subtitle = font_small.render("Creative Coding with Python", True, (255, 255, 255))
            line1 = font_small.render("Students learn digital animation, 2D game design,", True, (255, 255, 255))
            line2 = font_small.render("and AI-inspired decision making through hands-on Python projects,", True, (255, 255, 255))
            line3 = font_small.render("ending with a student-designed interactive game.", True, (255, 255, 255))
            prompt = font_small.render("Click / tap or press any key to begin", True, (255, 255, 0))

            center_x = WIDTH // 2
            y = 120
            for surf in [title, subtitle, line1, line2, line3, prompt]:
                rect = surf.get_rect(center=(center_x, y))
                screen.blit(surf, rect)
                y += 50

        else:
            # Game objects
            stickman_guy.draw(screen)
            obstacle_box.draw(screen)

            # Score
            score_surf = font_small.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_surf, (10, 10))

            if state == "game_over":
                over_surf = font_large.render("GAME OVER!", True, (255, 0, 0))
                prompt_surf = font_small.render(
                    "Click / tap or press any key to play again",
                    True,
                    (255, 255, 255),
                )
                over_rect = over_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
                prompt_rect = prompt_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
                screen.blit(over_surf, over_rect)
                screen.blit(prompt_surf, prompt_rect)

        pygame.display.flip()
        
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
