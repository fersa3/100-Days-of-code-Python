import pygame

class Barrier:
    def __init__(self, screen, image_path, dimensions, x):
        """ Load the image and get its rectangle """
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size=dimensions)
        self.player_pos = pygame.Vector2(x, screen.get_height() * 5/8 )
        # Rectangle for collision detection and alignment.
        self.rect = self.image.get_rect(topleft=(self.player_pos.x, self.player_pos.y))
        self.collision_count = 0


    def draw(self, screen):
        """ Draw the spaceship at player_pos """
        screen.blit(self.image, self.rect)

    def detect_5_collisions(self, bullets):
        """ Check for collisions with bullets and update the count. If 5 collisions are detected, remove the rock. """
        # If the input object is not a list, turn it into a list:
        if not isinstance(bullets, list):
            bullets = [bullets]
        for bullet in bullets[:]:
            if self.rect.colliderect(bullet):
                self.collision_count += 1
                bullet.fired = False
                bullets.remove(bullet)
            if self.collision_count >= 5:
                return True
        return False

