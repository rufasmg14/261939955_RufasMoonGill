import pygame
import os
import time
import random
from pygame import mixer
pygame.mixer.init()
pygame.font.init()

WIDTH, HEIGHT = 700, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Shoot")

# enemy ship
ENEMY_SHIP = pygame.image.load(os.path.join("assets", "enemy.png"))

#Asteroid
ASTEROID_IMAGE = pygame.image.load(os.path.join('assets', 'asteroid.png'))

# Player 
player_ship = pygame.image.load(os.path.join("assets", "spaceship.png"))

# Lasers
ENEMY_LASER = pygame.image.load(os.path.join("assets", "enemyL.png"))
PLAYER_LASER = pygame.image.load(os.path.join("assets", "PlayerL.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")), (WIDTH, HEIGHT))

bullteSound = pygame.mixer.Sound(os.path.join("assets", "shoot.mp3"))
music = pygame.mixer.music.load(os.path.join("assets", "song.mp3"))
pygame.mixer.music.play(-1)

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

class SpaceShip:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

score_font = pygame.font.SysFont("comicsans", 30)
class Player(SpaceShip):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = player_ship
        self.laser_img = PLAYER_LASER
        self.bullets = []
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = 0

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            self.score += 15

    def move_bullets(self, vel, asteroids):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for asteroid in asteroids:
                    if laser.collision(asteroid):
                        asteroids.remove(asteroid)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            self.score += 10

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        score_label = score_font.render(f"Score: {self.score}", 1, (255, 255, 255))
        window.blit(score_label, (10, 50))

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Asteroid:
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.vel = random.randint(1, 2)
        self.asteroid_img = ASTEROID_IMAGE
        self.mask = pygame.mask.from_surface(self.asteroid_img)

    def draw(self, window):
        window.blit(self.asteroid_img, (self.x, self.y))

    def move(self):
        self.y += self.vel

    def off_screen(self, height):
        return self.y >= height

    def collision(self, obj):
        return collide(self, obj)


class Enemy(SpaceShip):
    COLOR_MAP = {
                "red": (ENEMY_SHIP, ENEMY_LASER),
                }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

class PowerUp:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self):
        return self.y >= HEIGHT

    def collision(self, obj):
        return collide(self, obj)


previous_score = 0
def main():
    global previous_score
    run = True
    FPS = 60
    level = -1
    lives = 5
    main_font = pygame.font.SysFont("Arial", 30)
    lost_font = pygame.font.SysFont("Arial", 60)

    enemies = []
    wave_length = 1
    enemy_vel = 0.5

    asteroids = []
    wave_length = 1
    asteroid_vel = 0.5

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    powerups = []
    powerup_vel = 3

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)
        
        for powerup in powerups:
            powerup.draw(WIN)

        for asteroid in asteroids:
            asteroid.draw(WIN)

        player.draw(WIN)


        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
                previous_score = player.score
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red"]))
                enemies.append(enemy)
        
        if len(asteroids) == 0:
            level += 1
            wave_length += 5
            for _ in range(wave_length):
                asteroid = Asteroid(random.randrange(50, WIDTH-100), random.randrange(-1500, -100))
                asteroids.append(asteroid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            bullteSound.play()
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)

        if len(powerups) == 0:
            powerup_x = random.randrange(50, WIDTH-100)
            powerup_y = random.randrange(-1500, -100)
            powerup_img = pygame.image.load(os.path.join("assets", "powerup.png"))
            powerup = PowerUp(powerup_x, powerup_y, powerup_img)
            powerups.append(powerup)

        for powerup in powerups[:]:
            powerup.move(powerup_vel)

            if powerup.off_screen():
                powerups.remove(powerup)
            elif powerup.collision(player):
                # Apply power-up effect to the player
                player.health += 20
                if player.health > player.max_health:
                    player.health = player.max_health
                powerups.remove(powerup)

        for asteroid in asteroids[:]:
            asteroid.move()
            if collide(asteroid, player):
                player.health -= 10
                asteroids.remove(asteroid)
            elif asteroid.y + asteroid.asteroid_img.get_height() > HEIGHT:
                lives -= 1
                asteroids.remove(asteroid)

        player.move_bullets(-laser_vel, asteroids)


def main_menu():
    title_font = pygame.font.SysFont("Arial", 70)
    previous_score_font = pygame.font.SysFont("Arial", 30)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("click to begin", 1, (255,255,255))
        previous_score_label = previous_score_font.render(f"Previous Score: {previous_score}", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        WIN.blit(previous_score_label, (WIDTH/2 - previous_score_label.get_width()/2, 450))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
