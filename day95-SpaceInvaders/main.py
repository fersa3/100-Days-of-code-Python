import pygame
from spaceship import Spaceship
from bullets import SpaceshipBullets
from barrier import Barrier
from aliens import Alien
from lives_manager import LivesManager
import random

# TODOs:
# 1: Create all objects. Spaceship, aliens, barrier and bullets.
# 2: Arrange aliens on the screen as separate objects from the same class. As well as the barrier.
# 3: Make the bullets move with the spaceship and generate a new bullet object each time "spacebar" is pressed.
# 4: Detect bullet collision with a barrier or alien object.
# 5: Make aliens move altogether randomly horizontally.
# 6: Make aliens shoot randomly.
# 7: Detect collisions with rocks & the spaceship.
# 8: Count and show player's life's. Show small spaceships representing lives in the bottom left.
# 8.1: Make the spaceship immune for a couple of seconds after it is reset.
# 9: Count and show score.
# 10: Detect and show Game over screen.
# Making things more interesting:
# TODO 11: Add Bonus UFO.
# TODO 12: Make the game more challenging by increasing alien speed or bullet frequency over time.
# TODO 13: Add sound effects for shooting, explosions, and collisions.
# TODO 14: Use animations for alien destruction or bullet impacts.
# TODO 15: If aliens_line list is empty, create a new one, lower and faster.

def display_game_over():
    """ Shows game over on the screen for 5 seconds. """
    font = pygame.font.SysFont("pressstart2pregular", 60)  # Create font object
    game_over_text = font.render("GAME OVER", True, "red")
    screen.blit(game_over_text, (X_MAX/2-game_over_text.get_width()/2, 100))
    pygame.display.update()
    pygame.time.delay(5000)


# pygame setup
pygame.init()
# Config variables:
X_MAX = 1280
DEFAULT_DIMENSIONS = (60, 60)
screen = pygame.display.set_mode((X_MAX, 720))
clock = pygame.time.Clock()
running = True
dt = 0
aliens_direction = 1
players_spaceship_img = "characters/spaceship.png"

# Initialize objects for game elements.
player = Spaceship(screen, players_spaceship_img, DEFAULT_DIMENSIONS)
spaceship_bullet = SpaceshipBullets(player.player_pos, DEFAULT_DIMENSIONS)
lives_manager = LivesManager(screen, players_spaceship_img, (0.5*DEFAULT_DIMENSIONS[0], 0.5*DEFAULT_DIMENSIONS[1]))
barrier_rocks = []
aliens_line = []
alien_bullets = []

for i in range(1, 5):
    x = (screen.get_width()-DEFAULT_DIMENSIONS[0]) * (i / 5) # For creating 4 rocks
    rock = Barrier(screen, "characters/asteroide.png", (1.5*DEFAULT_DIMENSIONS[0], 1.5*DEFAULT_DIMENSIONS[1]), x)
    barrier_rocks.append(rock)
for line in range(3, 0, -1):
    for i in range(1,10):
        x_cor = (screen.get_width() * (i / 10)) # For creating 9 aliens
        y_cor = (screen.get_height() * (3-line) / 10) + 50
        alien = Alien(f"characters/alien{line}.png", DEFAULT_DIMENSIONS, x_cor, y_cor, line)
        aliens_line.append(alien)

explosion_start_time = None  # To track when spaceship explosion begins and freeze the screen for 2 seconds.

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # Draw the spaceship, and lives_manager objects:
    spaceship_bullet.move_with_spaceship(player.player_pos, DEFAULT_DIMENSIONS)
    player.draw(screen)
    lives_manager.draw(screen)
    player.display_score(screen)

    # Create aliens and barrier:
    for rock in barrier_rocks:
        rock.draw(screen)
        # If 5 collisions are detected with a rock from the barrier, remove the rock.
        if rock.detect_5_collisions(alien_bullets) or rock.detect_5_collisions(spaceship_bullet):
            barrier_rocks.remove(rock)

    # Check if any alien hits a boundary:
    for alien in aliens_line:
        if alien.rect.right >= X_MAX and aliens_direction == 1:
            aliens_direction = -1
            # Move down the entire block each time it reaches the border (has to be done 1 by 1):
            for al in aliens_line:
                al.move(0,10)
            break # To stop checking
        elif alien.rect.left <= 0 and aliens_direction == -1:
            aliens_direction = 1
            # Move down the entire block each time it reaches the border (has to be done 1 by 1):
            for al in aliens_line:
                al.move(0,10)
            break  # To stop checking

    # Aliens to move together and bounce left and right.
    for alien in aliens_line:
        alien.move(aliens_direction)
        alien.draw(screen)

    # Loop trough each alien and choose randomly which alien shoots.
    for alien in aliens_line:
        max_bullets_per_alien = 3
        active_bullets_per_alien = [bullet for bullet in alien.bullets if bullet.fired]
        shooting_probability = random.choice(range(1000))
        if shooting_probability == 1:  # 1/100 per alien
            # Only fire if the alien has less than max_bullets_per_alien
            if len(active_bullets_per_alien) < max_bullets_per_alien:
                shooter = alien.create_bullets(DEFAULT_DIMENSIONS)
                alien_bullets.append(shooter)

    for a_bullet in alien_bullets:
        a_bullet.fire()
        a_bullet.draw(screen)
        # Remove active bullets that leave the screen per alien.
        if a_bullet.rect.top > screen.get_height():
            alien_bullets.remove(a_bullet)
            a_bullet.parent_alien.bullets.remove(a_bullet)

    # Detect collision with alien, remove the alien from the list & update player's score.
    collisions_alien = spaceship_bullet.collision_with_alien(aliens_line)
    for collision in collisions_alien:
        aliens_line.remove(collision)
        player.score += collision.points

    # Spaceship movement, loose lives and game over handling:
    if explosion_start_time:
        if pygame.time.get_ticks() - explosion_start_time >= 2000:  # If an explosion is active, check if 2 seconds have passed
            explosion_start_time = None  # Reset the explosion timer
            if lives_manager.loose_live() > 0:
                player.reset_position(screen, players_spaceship_img, DEFAULT_DIMENSIONS)
            else:
                display_game_over()
                running = False  # Stop the game
        else:
            screen.blit(player.image, player.rect) # Continue displaying the explosion image
            pygame.time.delay(2000)
    else:
        if not player.detect_collision_bullet(alien_bullets, screen, DEFAULT_DIMENSIONS):
            keys = pygame.key.get_pressed()
            player.move(keys, player, dt)
            spaceship_bullet.fire(screen, keys)
            if any(alien.alien_pos.y >= (screen.get_height()-100-DEFAULT_DIMENSIONS[1]) for alien in aliens_line):
                display_game_over()
                running = False
        else:
            explosion_start_time = pygame.time.get_ticks()  # Trigger the explosion and start the timer

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()