import colorsys
import asyncio
import pygame as py
import random
import time

py.font.init()
py.init()

WINDOW_SIZE = (800, 600)
WIDTH, HEIGHT = WINDOW_SIZE
PLAYER_WIDTH, PLAYER_HEIGHT = 20, 45
PLAYER_VEL = 5
BG_IMAGE_PATH = "Images/bg-tiles.png"
FONT_FAMILY = "Fonts/SUPERDIG.TTF"
GIRL_ENEMY_WIDTH, GIRL_ENEMY_HEIGHT = 20, 45
MAX_TIME_LEVEL = 15000

class WaterObstacle:
    def __init__(self, x, y, width, height):
        self.rect = py.Rect(x, y, width, height)
        self.image = py.transform.scale(py.image.load('Images/shower_sprite.png'), (width, height))

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))

    @classmethod
    def generate_random_obstacles(cls, num_obstacles, player, walls, min_distance):
        obstacles = []
        width, height = 37, 50
        while len(obstacles) < num_obstacles:
            x = random.randint(0, WIDTH - width)
            y = random.randint(0, HEIGHT - height)
            obstacle = cls(x, y, width, height)
            if (not obstacle.rect.colliderect(player.rect) and
                not obstacle.rect.collidelistall([wall.rect for wall in walls]) and
                not obstacle.rect.collidelistall([obstacle.rect for obstacle in obstacles]) and
                ((obstacle.rect.x - player.rect.x)**2 + (obstacle.rect.y - player.rect.y)**2)**0.5 >= min_distance):
                obstacles.append(obstacle)
        return obstacles

class Wall:

    def __init__(self, x, y, width, height):
        self.rect = py.Rect(x, y, width, height)

    def draw(self, win):
        py.draw.rect(win, (0, 0, 0), self.rect)

    @classmethod
    def generate_random_walls(cls, num_walls, wall_min_size, wall_max_size, player):
        walls = [
            cls(0, 0, WIDTH, 30),
            cls(0, 0, 30, HEIGHT),
            cls(WIDTH - 30, 0, 30, HEIGHT),
            cls(0, HEIGHT - 30, WIDTH, 30),
        ]
        while len(walls) < num_walls + 4:
            width = random.randint(wall_min_size, wall_max_size) // PLAYER_VEL * PLAYER_VEL
            height = random.randint(wall_min_size, wall_max_size) // PLAYER_VEL * PLAYER_VEL
            x = random.randint(0, (WIDTH - width) // PLAYER_VEL) * PLAYER_VEL
            y = random.randint(0, (HEIGHT - height) // PLAYER_VEL) * PLAYER_VEL
            wall = cls(x, y, width, height)
            if not wall.rect.colliderect(player.rect):
                walls.append(wall)
        return walls

class Player:

    def __init__(self, x, y, width, height, vel):
        self.rect = py.Rect(x, y, width, height)
        self.image = py.transform.scale(py.image.load('Images/character_front_sprite.png'), (width, height))
        self.vel = vel

    def set_image(self, image):
        self.image = image

    def set_velocity(self, vel):
        self.vel = vel

    def get_velocity(self):
        return self.vel

    def check_wall_colisions(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                return True
        return False

    def check_obstacle_colisions(self, obstacles):
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                return True
        return False

    def check_bag_colision(self, bag):
        if self.rect.colliderect(bag.rect):
            return True
        return False

    def check_fries_colision(self, fries):
        if self.rect.colliderect(fries.rect):
            return True
        return False

    def move(self, keys, walls):
        if (keys[py.K_a] or keys[py.K_LEFT]) and self.rect.x - self.vel > 0:
            self.rect.x -= self.vel
            if self.check_wall_colisions(walls):
                self.rect.x += self.vel
        if (keys[py.K_d] or keys[py.K_RIGHT]) and self.rect.x + self.vel + self.rect.width < WIDTH:
            self.rect.x += self.vel
            if self.check_wall_colisions(walls):
                self.rect.x -= self.vel
        if (keys[py.K_w] or keys[py.K_UP]) and self.rect.y - self.vel > 0:
            self.rect.y -= self.vel
            if self.check_wall_colisions(walls):
                self.rect.y += self.vel
        if (keys[py.K_s] or keys[py.K_DOWN]) and self.rect.y + self.vel + self.rect.height < HEIGHT:
            self.rect.y += self.vel
            if self.check_wall_colisions(walls):
                self.rect.y -= self.vel

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))

class GirlEnemy:
    def __init__(self, x, y, width=GIRL_ENEMY_WIDTH, height=GIRL_ENEMY_HEIGHT, vel=1):
        self.rect = py.Rect(x, y, width, height)
        self.image = py.transform.scale(py.image.load('Images/girl-enemy-sprite.png'), (width, height))
        self.vel = vel

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))

    @classmethod
    def spawn_random(cls, player, walls, water_obstacles, bag, fries):
        max_distance = -1
        girl_enemy_pos = (-1, -1)
        for i in range(10):
            attempts = 0
            max_attempts = 1000
            while attempts < max_attempts:
                attempts += 1
                x = random.randint(30, WIDTH-30)
                y = random.randint(30, HEIGHT-30)
                rect = py.Rect(x, y, GIRL_ENEMY_WIDTH, GIRL_ENEMY_HEIGHT)
                if rect.colliderect(player.rect):
                    continue
                if rect.collidelistall([wall.rect for wall in walls]) or rect.collidelist([obstacle.rect for obstacle in water_obstacles]):
                    continue

                distance = ((((player.rect.x - x) ** 2 + (player.rect.y - y) ** 2) ** 0.5) * 3 + ((bag.rect.x - x) ** 2 + (bag.rect.y - y) ** 2) ** 0.5 + ((fries.rect.x - x) ** 2 + (fries.rect.y - y) ** 2) ** 0.5) / 5
                if distance > max_distance:
                    max_distance = distance
                    girl_enemy_pos = (x, y)
                break

        if girl_enemy_pos == (-1, -1):
            return None
        girl_enemy = cls(*girl_enemy_pos)
        return girl_enemy

    def move(self, player, walls):
        if self.rect.x < player.rect.x:
            self.rect.x += self.vel
            if self.rect.collidelistall([wall.rect for wall in walls]):
                self.rect.x -= self.vel
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.vel
            if self.rect.collidelistall([wall.rect for wall in walls]):
                self.rect.x += self.vel
        if self.rect.y < player.rect.y:
            self.rect.y += self.vel
            if self.rect.collidelistall([wall.rect for wall in walls]):
                self.rect.y -= self.vel
        elif self.rect.y > player.rect.y:
            self.rect.y -= self.vel
            if self.rect.collidelistall([wall.rect for wall in walls]):
                self.rect.y += self.vel

class Fries:
    def __init__(self, x, y):
        self.rect = py.Rect(x, y, 50, 50)
        self.image = py.transform.scale(py.image.load("Images/fries_sprite.png"), (50, 50))

    def remove(self):
        self.rect.x = -100
        self.rect.y = -100

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))


    @classmethod
    def generate_random_fries_location(cls, player, walls, water_obstacles, bag):
        width, height = 50, 50
        fries_list = []
        for i in range(5):
            while True:
                x = random.randint(0, WIDTH - width)
                y = random.randint(0, HEIGHT - height)
                fries = cls(x, y)
                if not fries.rect.colliderect(player.rect) and not fries.rect.collidelistall([wall.rect for wall in walls]) and not fries.rect.collidelistall([obstacle.rect for obstacle in water_obstacles]) and not fries.rect.colliderect(bag.rect):
                    fries_list.append(fries)
                    break
        max_dist_fries = fries_list[0]
        max_dist = ((max_dist_fries.rect.x - player.rect.x)**2 + (max_dist_fries.rect.y - player.rect.y)**2)**0.5 + ((max_dist_fries.rect.x - bag.rect.x)**2 + (max_dist_fries.rect.y - bag.rect.y)**2)**0.5
        for fries in fries_list:
            dist = ((fries.rect.x - player.rect.x)**2 + (fries.rect.y - player.rect.y)**2)**0.5 + ((fries.rect.x - bag.rect.x)**2 + (fries.rect.y - bag.rect.y)**2)**0.5
            if dist > max_dist:
                max_dist = dist
                max_dist_fries = fries

        return max_dist_fries

class Deodorant:
    speed = 5

    def __init__(self, x, y, orientation):
        self.orientation = orientation
        if orientation == 'left' or orientation == 'right':
            self.rect = py.Rect(x, y, 30, 10)
            self.image = py.transform.rotate(py.transform.scale(py.image.load('Images/deodorant_sprite.png'), (10, 30)), 90)
        else:
            self.rect = py.Rect(x, y, 10, 30)
            self.image = py.transform.scale(py.image.load('Images/deodorant_sprite.png'), (10, 30))

    def set_speed(self, speed):
        self.speed = speed

    def draw(self, win):
        win.blit(self.image, self.rect)

    def move(self):
        if self.orientation == 'up':
            self.rect.y -= self.speed
        elif self.orientation == 'down':
            self.rect.y += self.speed
        elif self.orientation == 'left':
            self.rect.x -= self.speed
        elif self.orientation == 'right':
            self.rect.x += self.speed

    @classmethod
    def launch_random(cls, player):
        orientation = random.choice(['up', 'down', 'left', 'right'])
        x, y = 0, 0
        match orientation:
            case 'up':
                x = player.rect.x
                y = HEIGHT
            case 'down':
                x = player.rect.x
                y = 0
            case 'left':
                x = WIDTH
                y = player.rect.y
            case 'right':
                x = 0
                y = player.rect.y

        return cls(x, y, orientation)

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = py.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.font = py.font.Font(FONT_FAMILY, 30)

    def draw(self, win):
        py.draw.rect(win, (255, 255, 255), self.rect)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        win.blit(text_surface, (self.rect.x + (self.rect.width - text_surface.get_width()) // 2, self.rect.y + (self.rect.height - text_surface.get_height()) // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Bag:
    def __init__(self, x, y, width=50, height=50):
        self.rect = py.Rect(x, y, width, height)
        self.image = py.transform.scale(py.image.load("Images/paper_bag_sprite.png"), (width, height))

    def draw(self, win):
        win.blit(self.image, (self.rect.x, self.rect.y))

    @classmethod
    def generate_random_bag(cls, player, walls, water_obstacles):
        width, height = 50, 50
        while True:
            x = random.randint(0, WIDTH - width)
            y = random.randint(0, HEIGHT - height)
            bag = cls(x, y, width, height)
            if not bag.rect.colliderect(player.rect) and not bag.rect.collidelistall(
                    [wall.rect for wall in walls]) and not bag.rect.collidelistall([obstacle.rect for obstacle in water_obstacles]):
                return bag

py.mixer.init()
py.mixer.music.load('Sounds/bg-music.ogg')
py.mixer.music.play(-1)
py.mixer.music.set_volume(0.1)

sound_effects = {
    'complete-level': py.mixer.Sound('Sounds/complete-level.ogg'),
    'hit': py.mixer.Sound('Sounds/hit.ogg'),
    'pickup-fries': py.mixer.Sound('Sounds/pickup-fries.ogg')
}
for sound in sound_effects.values():
    sound.set_volume(0.1)

WIN = py.display.set_mode(WINDOW_SIZE)
py.display.set_caption("Put the fries in the bag!")
BG = py.image.load(BG_IMAGE_PATH)
FONT = py.font.SysFont(FONT_FAMILY, 30)
WATER_SPAWN_MIN_DISTANCE = 100
max_time_level = MAX_TIME_LEVEL
deodorant_launch_event_speed = 3000
deodorant_speed = 5

#Events:
DEODORANT_LAUNCH_EVENT = py.USEREVENT + 1
RESET_DEODORANT_LAUNCH_TIME_EVENT = py.USEREVENT + 2

async def main():
    await main_menu(WIN)
    run = True
    game_paused = False
    score = 0
    high_score = 0
    player_start_x = WIDTH // 2 - PLAYER_WIDTH // 2
    player_start_y = HEIGHT // 2 - PLAYER_HEIGHT // 2
    player = Player(player_start_x, player_start_y, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_VEL)
    clock = py.time.Clock()
    start_time = time.time()
    timer_start = py.time.get_ticks()
    walls, water_obstacles, bag, fries, enemy_girl = generate_level(10, 3, player, WATER_SPAWN_MIN_DISTANCE, score)
    player_can_pass = False
    launch_deodorant = False
    play_sound_effects = True
    py.time.set_timer(DEODORANT_LAUNCH_EVENT, 999999999)
    remaining_deodorant_time = deodorant_launch_event_speed
    deodorant = Deodorant(-1, -1, 'up')
    bg_saturation = 0.2
    while run:
        clock.tick(60)
        await asyncio.sleep(0)
        elapsed_time = time.time() - start_time
        t = elapsed_time / 10
        bg_color = get_background_underlay(t, bg_saturation)

        level_time = max_time_level - (py.time.get_ticks() - timer_start)
        if level_time <= 0 and not game_paused:
            sound_effects['hit'].play()
            action = await game_over_screen(WIN, score, high_score)
            game_paused = False
            if action == 'exit':
                run = False
                break
            else:
                score, player_can_pass, launch_deodorant, timer_start, bg_saturation = reset_game(player, score, player_can_pass, launch_deodorant, timer_start, bg_saturation, deodorant)
                reset_difficulty()
                walls, water_obstacles, bag, fries, enemy_girl = generate_level(10, 3, player, WATER_SPAWN_MIN_DISTANCE, score)

        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
                break
            elif event.type == DEODORANT_LAUNCH_EVENT and not game_paused:
                deodorant = Deodorant.launch_random(player)
                deodorant.set_speed(deodorant_speed)
                launch_deodorant = True
            elif event.type == py.KEYDOWN and event.key == py.K_ESCAPE:
                game_paused = not game_paused
                if game_paused:
                    pause_time_start = py.time.get_ticks()
                    remaining_deodorant_time = deodorant_launch_event_speed - int(((time.time() - start_time) * 1000)) % deodorant_launch_event_speed
                    py.time.set_timer(DEODORANT_LAUNCH_EVENT, 999999999)
                else:
                    if score >= 1:
                        py.time.set_timer(DEODORANT_LAUNCH_EVENT, remaining_deodorant_time)
                        py.time.set_timer(RESET_DEODORANT_LAUNCH_TIME_EVENT, remaining_deodorant_time)
                    timer_start += py.time.get_ticks() - pause_time_start
            elif event.type == RESET_DEODORANT_LAUNCH_TIME_EVENT:
                py.time.set_timer(DEODORANT_LAUNCH_EVENT, deodorant_launch_event_speed)
                py.time.set_timer(RESET_DEODORANT_LAUNCH_TIME_EVENT, 999999999)
            elif event.type == py.KEYDOWN and event.key == py.K_m:
                py.mixer.music.set_volume(0.0 if py.mixer.music.get_volume() > 0.0 else 0.1)
            elif event.type == py.KEYDOWN and event.key == py.K_n:
                for sound in sound_effects.values():
                    sound.set_volume(0.0 if sound.get_volume() > 0.0 else 0.1)

        if game_paused:
            draw_pause_screen(WIN, bg_color)
            py.display.update()
            continue

        keys = py.key.get_pressed()
        player.move(keys, walls)

        if player.check_fries_colision(fries):
            fries.remove()
            sound_effects['pickup-fries'].play()
            player.set_image(py.transform.scale(py.image.load('Images/character_with_fries_sprite.png'), (PLAYER_WIDTH, PLAYER_HEIGHT)))
            player_can_pass = True

        if player.check_bag_colision(bag) and player_can_pass:
            sound_effects['complete-level'].play()
            score += 1
            if score == 1:
                py.time.set_timer(DEODORANT_LAUNCH_EVENT, deodorant_launch_event_speed)
            bg_saturation = min(0.8, bg_saturation + 0.02)
            player.set_image(py.transform.scale(py.image.load('Images/character_front_sprite.png'), (PLAYER_WIDTH, PLAYER_HEIGHT)))
            if score % 5 == 0:
                update_difficulty(DEODORANT_LAUNCH_EVENT)
            high_score = max(score, high_score)
            timer_start = py.time.get_ticks()
            player_can_pass = False
            walls, water_obstacles, bag, fries, enemy_girl = generate_level(10, 3, player, WATER_SPAWN_MIN_DISTANCE, score)

        if player.check_obstacle_colisions(water_obstacles) or player.rect.colliderect(enemy_girl.rect):
            sound_effects['hit'].play()
            action = await game_over_screen(WIN, score, high_score)
            game_paused = False
            if action == 'exit':
                run = False
                break
            else:
                score, player_can_pass, launch_deodorant, timer_start, bg_saturation = reset_game(player, score, player_can_pass, launch_deodorant, timer_start, bg_saturation, deodorant)
                reset_difficulty()
                walls, water_obstacles, bag, fries, enemy_girl = generate_level(10, 3, player, WATER_SPAWN_MIN_DISTANCE, score)

        if launch_deodorant and deodorant.rect.colliderect(player.rect):
            sound_effects['hit'].play()
            action = await game_over_screen(WIN, score, high_score)
            game_paused = False
            if action == 'exit':
                run = False
                break
            else:
                score, player_can_pass, launch_deodorant, timer_start, bg_saturation = reset_game(player, score, player_can_pass, launch_deodorant, timer_start, bg_saturation, deodorant)
                reset_difficulty()
                walls, water_obstacles, bag, fries, enemy_girl = generate_level(10, 3, player, WATER_SPAWN_MIN_DISTANCE, score)
        if not game_paused:
            draw_sprites(player, player_can_pass, bg_color, walls, water_obstacles, bag, fries, launch_deodorant, deodorant)
            draw_text(score, high_score, timer_start)
            draw_enemy_girl(enemy_girl, player, walls)
        py.display.update()

    py.quit()

def get_background_underlay(t, saturation=0.2):
    r, g, b = colorsys.hsv_to_rgb(t % 1, saturation, 1)
    return int(r * 255), int(g * 255), int(b * 255)

def generate_level(num_walls, num_obstacles, player, min_distance, score):
    walls = Wall.generate_random_walls(num_walls, 50, 100, player)
    water_obstacles = WaterObstacle.generate_random_obstacles(num_obstacles, player, walls, min_distance)
    bag = Bag.generate_random_bag(player, walls, water_obstacles)
    fries = Fries.generate_random_fries_location(player, walls, water_obstacles, bag)
    if score >= 5:
        enemy_girl = GirlEnemy.spawn_random(player, walls, water_obstacles, bag, fries)
    else:
        enemy_girl = GirlEnemy(-100, -100, vel=0)
    return walls, water_obstacles, bag, fries, enemy_girl

def reset_game(player, score, player_can_pass, launch_deodorant, timer_start, bg_saturation, deodorant):
    bg_saturation = 0.2
    player.rect.x = WIDTH // 2 - PLAYER_WIDTH // 2
    player.rect.y = HEIGHT // 2 - PLAYER_HEIGHT // 2
    player.set_image(py.transform.scale(py.image.load('Images/character_front_sprite.png'), (PLAYER_WIDTH, PLAYER_HEIGHT)))
    score = 0
    global DEODORANT_LAUNCH_EVENT
    py.time.set_timer(DEODORANT_LAUNCH_EVENT, 999999999)
    player_can_pass = False
    launch_deodorant = False
    deodorant.rect.x = -1
    deodorant.rect.y = -1
    timer_start = py.time.get_ticks()
    return score, player_can_pass, launch_deodorant, timer_start, bg_saturation

def draw_sprites(player, player_can_pass, color, walls, water_obstacles, bag, fries, launch_deodorant, deodorant):
    WIN.fill(color)
    for i in range(0, WINDOW_SIZE[0], BG.get_width()):
        for j in range(0, WINDOW_SIZE[1], BG.get_height()):
            WIN.blit(BG, (i, j))

    for wall in walls:
        wall.draw(WIN)
    for water_obstacle in water_obstacles:
        water_obstacle.draw(WIN)
    bag.draw(WIN)
    if not player_can_pass:
        fries.draw(WIN)
    player.draw(WIN)

    if launch_deodorant:
        deodorant.draw(WIN)
        deodorant.move()
        if not(0 <= deodorant.rect.x <= WIDTH and 0 <= deodorant.rect.y <= HEIGHT):
            launch_deodorant = False

def draw_text(score, high_score, timer_start):
    score_text = FONT.render("Score: " + str(score), 1, (255, 255, 255))
    WIN.blit(score_text, (10, 0))

    global max_time_level
    elapsed_time = py.time.get_ticks() - timer_start
    remaining_time = max(0, max_time_level - elapsed_time)
    if remaining_time / 1000 > 5:
        timer_text = FONT.render(str(round(remaining_time / 1000, 1)), 1, (255, 255, 255))
        timer_title = FONT.render("Time left: ", 1, (255, 255, 255))
    else:
        timer_text = FONT.render(str(round(remaining_time / 1000, 1)), 1, (255, 0, 0))
        timer_title = FONT.render("Time left: ", 1, (255, 0, 0))

    WIN.blit(timer_title, (WIDTH - timer_title.get_width() - 55, 0))
    WIN.blit(timer_text, (WIDTH - timer_text.get_width() - 10, 0))

    high_score_text = FONT.render("High Score: " + str(high_score), 1, (255, 255, 255))
    WIN.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 0))


    text = FONT.render("'M': mute/unmute music | 'N': mute/unmute sound effects | 'ESC': pause/unpause", 1, (255, 255, 255))
    WIN.blit(text, (10, HEIGHT - text.get_height()))

def draw_enemy_girl(enemy_girl, player, walls):
    enemy_girl.draw(WIN)
    enemy_girl.move(player, walls)

def update_difficulty(DEODORANT_LAUNCH_EVENT):
    global max_time_level, deodorant_launch_event_speed, deodorant_speed
    max_time_level = max(7500, max_time_level - 500)
    deodorant_speed = min(8, deodorant_speed + 1)
    py.time.set_timer(DEODORANT_LAUNCH_EVENT, max(deodorant_launch_event_speed - 500, 1000))

def reset_difficulty():
    global WATER_SPAWN_MIN_DISTANCE
    WATER_SPAWN_MIN_DISTANCE = 100
    global max_time_level, deodorant_launch_event_speed, deodorant_speed
    max_time_level = MAX_TIME_LEVEL
    deodorant_launch_event_speed = 3000
    deodorant_speed = 5

def draw_pause_screen(win, bg_color):
    win.fill(bg_color)

    font = py.font.Font(FONT_FAMILY, 80)
    pause_text = font.render("Paused", True, (255 - bg_color[0], 255 - bg_color[1], 255 - bg_color[2]))
    win.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - pause_text.get_height() // 2))

    font = py.font.Font(FONT_FAMILY, 40)
    pause_text = font.render("Press escape to unpause", True, (0, 0, 0))
    win.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - pause_text.get_height() // 2 + 100))

async def main_menu(win):
    run = True
    main_menu_bg = py.transform.scale2x(py.image.load('Images/main_menu_bg.png'))
    while run:
        await asyncio.sleep(0)
        win.blit(main_menu_bg, (0, 0))
        py.font.init()
        font = py.font.Font(FONT_FAMILY, 40)
        text = font.render('Press any key to start...', 1, (255, 0, 0))
        win.blit(text, (WIDTH - text.get_width() - 50, HEIGHT - text.get_height() - 20))

        font = py.font.Font(FONT_FAMILY, 70)
        text = font.render('Put the Fries' , 1, (255, 0, 0))
        win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2 - 200))
        text = font.render('in the Bag!', 1, (255, 0, 0))
        win.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2 - 150))

        wasd_keys_image = py.transform.scale(py.image.load('Images/wasd.png'), (100, 100))
        win.blit(wasd_keys_image, (WIDTH//2 - wasd_keys_image.get_width()//2 - 100, HEIGHT//2 - wasd_keys_image.get_height()//2))

        esc_key_image = py.transform.scale(py.image.load('Images/esc.png'), (50, 50))
        win.blit(esc_key_image, (WIDTH//2 + esc_key_image.get_width()//2 + 100, HEIGHT//2 - esc_key_image.get_height()//2))

        font = py.font.Font(FONT_FAMILY, 30)
        text = font.render('TO MOVE', 1, (0, 0, 0))
        win.blit(text, (WIDTH//2 - wasd_keys_image.get_width()//2 - 100 - (text.get_width() - wasd_keys_image.get_width())//2, HEIGHT//2 - text.get_height()//2 + 50))

        text = font.render('TO PAUSE', 1, (0, 0, 0))
        win.blit(text, (WIDTH//2 + esc_key_image.get_width()//2 + 100 - (text.get_width() - esc_key_image.get_width())//2, HEIGHT//2 - text.get_height()//2 + 50))

        py.display.update()
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
            if event.type == py.KEYDOWN:
                run = False

async def game_over_screen(win, score, high_score):
    win.fill((0, 0, 0))  # Fill the screen with black
    font = py.font.Font(FONT_FAMILY, 50)
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    win.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() - 200))
    win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - score_text.get_height() // 2 - 100))
    win.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 - high_score_text.get_height() // 2))

    restart_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 50, "Restart [Enter]", "restart")

    restart_button.draw(win)
    py.display.update()

    while True:
        await asyncio.sleep(0)
        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                return "exit"
            if event.type == py.MOUSEBUTTONDOWN:
                if restart_button.is_clicked(event.pos):
                    return "restart"
            if event.type == py.KEYDOWN:
                if event.key == py.K_RETURN:
                    return "restart"

asyncio.run(main())