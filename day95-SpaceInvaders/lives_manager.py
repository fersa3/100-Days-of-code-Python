import pygame

class LivesManager:
    def __init__(self, screen, image_path, dimensions, initial_lives=3):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size=dimensions)
        self.lives = initial_lives
        self.game_over_display_time = 0


    def draw(self, screen):
        """ Draw len(self.lives)-1 small spaceships at the left bottom corner of the screen. """
        for live in range(self.lives-1):
            x = 30 + 40*live
            y = screen.get_height() - 50
            screen.blit(self.image, (x,y))

    def loose_live(self):
        """ Takes 1 life from self.lives """
        self.lives -= 1
        return self.lives

    def reset_lives(self, initial_lives=3):
        """ Resets initial lives to 3. """
        self.lives = initial_lives
