import pygame

class Bullets:
    def __init__(self, position, dimensions):
        left = position[0] + dimensions[0] / 2 - 2.5
        top = position[1] + dimensions[1] / 2
        width = 5
        height = 15
        self.rect = pygame.Rect(left, top, width, height)
        self.fired = False

class SpaceshipBullets(Bullets):
    def __init__(self, position, dimensions):
        super().__init__(position, dimensions)

    def move_with_spaceship(self, player_pos, dimensions):
        """ Makes the bullet move with the spaceship to it gets fired in the correct position. """
        # Get spaceship's position and place the bullet object if bullet's not been fired.
        if not self.fired:
            self.rect.left = player_pos[0] + dimensions[0] / 2 - 2.5
            self.rect.top = player_pos[1] + dimensions[1] / 2

    def fire(self, screen, keys):
        """ Fires a bullet up. """
        # Then move upwards on "spacebar" press.
        if keys[pygame.K_SPACE] and not self.fired:
            self.fired = True
        if self.fired:
            pygame.draw.rect(screen, color="white", rect=self.rect)
            self.rect = pygame.Rect.move(self.rect, 0, -3)
            # Reset fired when bullet is off the screen.
            if self.rect.top < 0:
                # if not self.bullet_on_screen:
                self.fired = False

    def collision_with_alien(self, aliens_list):
        """ Detects when a bullets has collided with an alien rect. """
        collisions = []
        for alien in aliens_list:
            if self.rect.colliderect(alien):
                collisions.append(alien)
                self.fired = False
        return collisions

class AlienBullets(Bullets):
    def __init__(self, position, dimensions, parent_alien):
        super().__init__(position, dimensions)
        self.parent_alien = parent_alien

    def draw(self, screen):
        """ Draws the bullet on the screen. """
        pygame.draw.rect(screen, color="white", rect=self.rect)

    def fire(self):
        """ Fires a bullet down. """
        # Then move downwards the bullet objects
        self.fired = True
        self.rect = pygame.Rect.move(self.rect, 0, 1)
        # Reset fired when bullet is off the screen.
        if self.rect.bottom < 0:
            # if not self.bullet_on_screen:
            self.fired = False
