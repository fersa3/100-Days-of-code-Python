import pygame

class Spaceship:
    def __init__(self, screen, image_path, dimensions):
        """ Load the image and get its rectangle """
        self.fired = None
        self.immunity_expiration_time = 0  # Timestamp until which the spaceship is immune to bullets.
        self.blink = False  # For activating blinking effect when immune.
        self.score = 0  # Initialize player's score.
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size=dimensions)
        self.player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() -100 )
        # Rectangle for collision detection and alignment.
        self.rect = self.image.get_rect(topleft=(self.player_pos.x, self.player_pos.y))

    def draw(self, screen):
        """ Draw the spaceship at player_pos """
        self.rect.topleft = self.player_pos
        if self.is_bullet_immune():
            if pygame.time.get_ticks() // 200 % 2 == 0:  # Time resolution 200 ms, and checks when the result is even.
                self.blink = True
                screen.blit(self.image, self.rect)
            else:
                self.blink = False
        else:
            screen.blit(self.image, self.rect)

    def move(self, keys, player, dt):
        """ Move the spaceship by adjusting its rect position """
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.player_pos.x -= 300 * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.player_pos.x += 300 * dt
        return self.player_pos

    def detect_collision_bullet(self, active_bullets, screen, dimensions):
        """ Detects when an alien bullet hits the spaceship and returns True """
        if self.is_bullet_immune():
            return False
        else:
            self.rect = self.image.get_rect(topleft=(self.player_pos.x, self.player_pos.y))
            for bullet in active_bullets:
                if bullet.rect.colliderect(self.rect):
                    self.image = pygame.image.load("characters/explosion1.png").convert_alpha()
                    self.image = pygame.transform.scale(self.image, size=dimensions)
                    screen.blit(self.image, self.rect)
                    return True
            return False

    def reset_position(self, screen, image_path, dimensions):
        """ Resets spaceship position and image """
        immune_duration: int = 2000
        self.player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() - 100)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size=dimensions)
        self.immunity_expiration_time = pygame.time.get_ticks() + immune_duration  # Current time + 2000

    def is_bullet_immune(self):
        """ If current time is less than the immunity expiration time, remains immune. """
        return pygame.time.get_ticks() < self.immunity_expiration_time

    def display_score(self, screen):
        """ Function to display the player's score. """
        font = pygame.font.SysFont("pressstart2pregular", 22)  # Create font object
        text = font.render(f"Score: {self.score}", True, "white")
        screen.blit(text, (25,15))
