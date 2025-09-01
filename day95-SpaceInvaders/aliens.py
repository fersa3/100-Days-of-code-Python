import pygame
from bullets import AlienBullets

class Alien:
    def __init__(self, image_path, dimensions, x_cor, y_cor, line):
        # Load the image and get its rectangle
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size=dimensions)
        self.alien_pos = pygame.Vector2(x_cor, y_cor)
        # Rectangle for collision detection and alignment.
        self.rect = self.image.get_rect(topleft=(self.alien_pos.x, self.alien_pos.y))
        self.bullets = []
        self.points = 10 * line

    def draw(self, screen):
        """ Draw the alien rect """
        screen.blit(self.image, self.rect)


    def move(self, x_offset, y_offset=0):
        """ Function to move the alien by an offset only in x. """
        self.rect.x += x_offset
        self.rect.y += y_offset
        self.alien_pos = pygame.Vector2(self.rect.x, self.rect.y)

    def create_bullets(self, dimensions):
        """ Create bullet object starting at the alien's position. """
        bullet = AlienBullets(self.alien_pos, dimensions, self)
        self.bullets.append(bullet)
        return bullet
