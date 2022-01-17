import os
import sys
import pygame
import time
import random

pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 30
WIDTH = 480
HEIGHT = 480

HP = 10
gold = 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
towers_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
projectiles_group = pygame.sprite.Group()
menu_group = pygame.sprite.Group()



def learn():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    fon = pygame.transform.scale(load_image('learn.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                start_screen()
                return
        pygame.display.flip()
        clock.tick(FPS)


def defeat():
    running = False
    fon = pygame.transform.scale(load_image('defeat.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
                towers_group.empty()
                enemies_group.empty()
                menu_group.empty()
                projectiles_group.empty()
                print(enemies_group)
                start_screen()
        pygame.display.flip()
        clock.tick(FPS)


def load_tiles(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    return image


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if name != 'learn.png':
        color_key = image.get_at((0, 0))
    image.set_colorkey(color_key)
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '0':
                Tile('grass', x, y)
            elif level[y][x] == '-':
                Tile('road_g', x, y)
            elif level[y][x] == '+':
                Tile('road_v', x, y)
            elif level[y][x] == '1':
                Tile('road_1', x, y)
            elif level[y][x] == '2':
                Tile('road_2', x, y)
            elif level[y][x] == '3':
                Tile('road_3', x, y)
            elif level[y][x] == '4':
                Tile('road_4', x, y)

    return x, y


def terminate():
    pygame.quit()
    sys.exit()


class Tile(pygame.sprite.Sprite):
    # Тайлы для карты
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Board:
    # Клетчатое поле для удобства
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * self.width for _ in range(self.height)]

    def get_cell(self, mouse_pos):
        # получаем номер клетки
        x, y = mouse_pos
        if y > 480 or x > 480:
            return None
        x_coord = x // 48
        y_coord = y // 48
        if y_coord > 10 or x_coord > 10:
            return None
        return x_coord, y_coord

    def on_click(self, cell_coords):
        return cell_coords

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        return self.on_click(cell)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.cycles = 0
        self.x, self.y = level_1[0][0] / 48, level_1[0][1] / 48
        self.frames = []
        self.sheet = load_image('error.png')
        self.cur_frame = 0
        self.turn = 1
        self.win = False
        self.HP = 2
        # Кол-во урона, которые нанесут пули, уже летящие за этим врагом
        self.bullets = 0
        self.timer = time.time()
        self.animation_delay = 0.15
        self.element = list()
        self.color = (0, 255, 0)
        self.move_speed = 1
        self.reaction_reload_timer = time.time()
        self.reaction_reload = False

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.width * i, self.rect.height * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        global HP
        # Враг дошел до конца
        if (self.rect.x, self.rect.y) == level_1[5] and not self.win:
            self.win = True
            enemies_group.remove(self)
            self.kill()
            HP -= 1
            return
        # Анимация
        if time.time() - self.timer > self.animation_delay:
            self.timer = time.time()
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        # Передвижение врага
        if not self.win:
            turn = level_1[self.turn - 1]
            next_turn = level_1[self.turn]
            if turn[0] < next_turn[0]:
                self.rect = self.rect.move(self.move_speed, 0)
            elif turn[0] > next_turn[0]:
                self.rect = self.rect.move(-self.move_speed, 0)
            elif turn[1] < next_turn[1]:
                self.rect = self.rect.move(0, self.move_speed)
            elif turn[1] > next_turn[1]:
                self.rect = self.rect.move(0, -self.move_speed)
            if (self.rect.x, self.rect.y) == level_1[self.turn]:
                self.turn += 1
        else:
            pass
        # Координаты
        self.x, self.y = self.rect.x // 48 + 1, self.rect.y // 48 + 1

        if self.HP <= 0:
            enemies_group.remove(self)
            self.kill()
        # HP bar
        if self.HP / 6 < 0.67:
            self.color = (255, 124, 0)
        if self.HP / 6 < 0.34:
            self.color = (255, 0, 0)
        if self.HP > 0:
            pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y - 10,
                                                  48 - 48 // 6 * (6 - self.HP), 7))
            pygame.draw.rect(screen, (0, 0, 0), (self.rect.x - 1, self.rect.y - 10, 49, 8), 1)

    def reaction(self, owner):
        global gold
        self.owner = owner
        if len(self.element) > 2:
            for i in range(len(self.element) - 2):
                self.element.remove(self.element[i + 2])
        if self.element[0] == self.element[1]:
            self.HP -= owner.atk / 2
            self.element.remove(self.element[1])
        # Вода по огню бьет намного больнее
        elif self.element[0] == 'fire' and self.element[1] == 'water':
            # X10 урон
            self.HP -= self.owner.atk * 10
            self.element.remove(self.element[1])

        elif 'fire' in self.element and 'water' in self.element:
            self.fire_water()

        elif 'fire' in self.element and 'earth' in self.element:
            self.fire_earth()

        elif 'fire' in self.element and 'electricity' in self.element:
            self.fire_electricity()

        elif 'water' in self.element and 'earth' in self.element:
            self.water_earth()

        elif 'water' in self.element and 'electricity' in self.element:
            self.water_electricity()

        elif 'earth' in self.element and 'electricity' in self.element:
            self.earth_electricity()

        else:
            self.HP -= owner.atk

        if self.HP <= 0:
            enemies_group.remove(self)
            self.kill()
            gold += 5

    def fire_water(self):
        # X2 урон
        self.HP -= self.owner.atk * 2
        self.element.remove(self.element[1])

    def fire_earth(self):
        # Оглушение врага на 2 сек
        self.fire_earth_timer = time.time()
        self.fire_earth_reaction = True
        self.HP -= self.owner.atk
        self.move_speed = 0
        self.element.remove(self.element[1])

    def fire_electricity(self):
        # С шансом 20% враг умирает от "перегрузки"
        self.HP -= self.owner.atk
        kill = random.randint(1, 5) == 5
        if kill:
            enemies_group.remove(self)
            self.kill()
        self.element.remove(self.element[1])

    def water_earth(self):
        # Небольшое оглушение + переодический урон(0,5) от "яда" 5 раз
        # *Перезарядка реакций начинается с момента проведения данной реакции и заканчивается в конце реакции
        if self.water_earth_reaction and not self.reaction_reload:
            self.move_speed = 1
            self.reaction_reload_timer = time.time()
            self.water_earth_reaction = False
            self.cycles = 0
        elif not self.water_earth_reaction and not self.reaction_reload:
            self.water_earth_reaction_timer = time.time()
            self.HP -= self.owner.atk
            self.reaction_reload = True
            self.water_earth_reaction = True
            self.move_speed = 0
            self.element.remove(self.element[1])
        else:
            self.HP -= self.owner.atk
            self.element.remove(self.element[1])

    def water_electricity(self):
        atk = self.owner.atk
        if self.element[1] == 'water':
            atk *= 3
        if self.reaction_reload:
            self.HP -= atk
        else:
            for enemy in enemies_group:
                if ('water' in enemy.element and self.owner.element == 'electricity') \
                        or ('electricity' in enemy.element and self.owner.element == 'water'):
                    if self.rect.collidepoint(enemy.rect.x, enemy.rect.y) \
                            or abs(self.rect.x - enemy.rect.x) < 65 and abs(self.rect.y - enemy.rect.y) < 65:
                        if enemy == self:
                            self.HP -= atk * 1.5
                        else:
                            enemy.HP -= atk * 1.5
            self.reaction_reload = True
            self.reaction_reload_timer = time.time()
            self.element.remove(self.element[1])

    def earth_electricity(self):
        self.HP -= self.owner.atk + self.HP / 5
        self.element.remove(self.element[1])


class Fire_Enemy(Enemy):
    def __init__(self):
        super().__init__()
        self.HP = 6
        self.element.append('fire')
        self.sheet = load_image('fire_enemy.png')
        self.cut_sheet(self.sheet, 4, 1)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.x * 48, self.y * 48)


class Storm_Enemy(Enemy):
    def __init__(self):
        super().__init__()
        self.HP = 6
        self.animation_delay = 0.1
        self.element.append('electricity')
        self.sheet = load_image('storm_enemy.png')
        self.cut_sheet(self.sheet, 4, 1)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.x * 48, self.y * 48)


class Earth_Enemy(Enemy):
    def __init__(self):
        super().__init__()
        self.HP = 6
        self.animation_delay = 0.12
        self.element.append('earth')
        self.sheet = load_image('earth_enemy.png')
        self.cut_sheet(self.sheet, 4, 1)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.x * 48, self.y * 48)


class Water_Enemy(Enemy):
    def __init__(self):
        super().__init__()
        self.HP = 6
        self.animation_delay = 0.12
        self.element.append('water')
        self.sheet = load_image('water_enemy.png')
        self.cut_sheet(self.sheet, 4, 1)
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(self.x * 48, self.y * 48)


class Projectile(pygame.sprite.Sprite):
    # Снаряды башен(пули)
    def __init__(self, sheet, columns, rows, x, y, owner, target):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.target = target
        self.x = x
        self.y = y
        self.timer = time.time()
        # Башня, которой принадлежит это снаряд
        self.owner = owner
        self.animation_delay = 0.08

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.width * i, self.rect.height * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        # Удаляем пулю, если target отсутствует(не состоит ни в одной группе)
        if not self.target.groups():
            self.kill()
        if time.time() - self.timer > self.animation_delay:
            self.timer = time.time()
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        # Передвижение
        x_dist = (self.target.rect.x - self.x + 12) / self.owner.bullet_speed
        y_dist = (self.target.rect.y - self.y + 12) / self.owner.bullet_speed
        self.rect = self.rect.move(x_dist, y_dist)
        collide = pygame.sprite.spritecollide(self, enemies_group, False)
        if collide:
            self.target.element.append(self.owner.element)
            self.target.reaction(self.owner)
            self.target.bullets -= self.owner.atk
            self.kill()


class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.columns = 4
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.sheet = load_image('error.png')
        self.rect = self.rect.move(x, y)
        self.x, self.y = x / 48, y / 48
        self.enemy_in_range = False
        self.enemies_list = list()
        self.timer = time.time()
        self.timer_2 = time.time()
        self.atk = 1
        self.animation_delay = 0.15
        self.atk_delay = 1
        # Чеб больше значение - тем меньше скорость снаряда
        self.bullet_speed = 17
        self.bullet_image = load_image('bullet.png')
        self.bullet_columns = 4

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.width * i, self.rect.height * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        if time.time() - self.timer_2 > self.animation_delay:
            self.timer_2 = time.time()
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        # Координаты.
        # для всех врагов
        for enemy in enemies_group:
            try:
                if self.enemies_list[0].win or not self.enemies_list[0].groups():
                    self.enemies_list.remove(self.enemies_list[0])
            except BaseException:
                pass
            # в радиусе данной башни
            if ((enemy.x + 1 == self.x and enemy.y + 1 == self.y) or
                (enemy.x == self.x and enemy.y + 1 == self.y) or
                (enemy.x - 1 == self.x and enemy.y + 1 == self.y) or
                (enemy.x - 1 == self.x and enemy.y == self.y) or
                (enemy.x - 1 == self.x and enemy.y - 1 == self.y) or
                (enemy.x == self.x and enemy.y - 1 == self.y) or
                (enemy.x + 1 == self.x and enemy.y - 1 == self.y) or
                (enemy.x + 1 == self.x and enemy.y == self.y)) \
                    and enemy.HP > 0 and enemy.HP - enemy.bullets > 0:
                # если враг до этого момента не был в радиусе башни, то добавляем и атакуем
                if enemy not in self.enemies_list:
                    self.enemies_list.append(enemy)
                if enemy in self.enemies_list:
                    if enemy == self.enemies_list[0]:
                        self.attack(enemy)
            else:
                # если не в радиусе башни, то пробуем удалить из списка врагов, которые в радиусе башни
                try:
                    self.enemies_list.remove(enemy)
                except BaseException:
                    pass

    def attack(self, enemy):
        if enemy.HP > 0:
            # проверка на уже летящие за врагом пули, чтобы не пускать лишние
            if enemy.HP - enemy.bullets > 0:
                if time.time() - self.timer > self.atk_delay:
                    self.timer = time.time()
                    bullet = Projectile(self.bullet_image, self.bullet_columns, 1,
                                        self.rect.x + 15, self.rect.y - 5, self, enemy)
                    projectiles_group.add(bullet)
                    enemy.bullets += self.atk
            else:
                print("bullets don't attack")
        else:
            self.enemies_list.remove(enemy)


class Fire_tower(Tower):
    def __init__(self, x, y):
        self.frames = []
        self.sheet = load_image('fire_tower1.png')
        self.columns = 11
        self.cut_sheet(self.sheet, self.columns, 1)
        super().__init__(x, y)
        self.atk = 2
        self.element = 'fire'
        self.bullet_image = load_image('fire_bullet.png')
        self.bullet_columns = 6


class Earth_tower(Tower):
    def __init__(self, x, y):
        self.frames = []
        self.sheet = load_image('earth_tower.png')
        self.columns = 8
        self.cut_sheet(self.sheet, self.columns, 1)
        super().__init__(x, y)
        self.atk = 3
        self.atk_delay = 2
        self.bullet_speed = 35
        self.element = 'earth'
        self.bullet_image = load_image('earth_bullet.png')
        self.bullet_columns = 4


class Storm_tower(Tower):
    def __init__(self, x, y):
        self.frames = []
        self.sheet = load_image('electro_tower.png')
        self.columns = 10
        self.cut_sheet(self.sheet, self.columns, 1)
        super().__init__(x, y)
        self.atk = 1
        self.atk_delay = 0.5
        self.element = 'electricity'
        self.bullet_image = load_image('electro_bullet.png')
        self.bullet_columns = 10


class Water_tower(Tower):
    def __init__(self, x, y):
        self.frames = []
        self.sheet = load_image('water_tower1.png')
        self.columns = 23
        self.cut_sheet(self.sheet, self.columns, 1)
        super().__init__(x, y)
        self.atk = 0.1
        self.atk_delay = 0.33
        self.element = 'water'
        self.bullet_image = load_image('water_bullet.png')
        self.bullet_columns = 6


class Select_menu(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x - 24, y - 24)
        self.x = x
        self.y = y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.width * i, self.rect.height * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self, xs, ys):
        global gold
        if self.rect.collidepoint(xs, ys):
            self.rect.collidepoint(xs, ys)
            if xs - 24 > self.x and ys - 24 > self.y and gold >= 50:
                tower = Water_tower(self.x, self.y)
                tower_place.append((self.x // 48, self.y // 48))
                towers_group.add(tower)
                self.kill()
                gold -= 50
            elif xs - 24 < self.x and ys - 24 > self.y and gold >= 50:
                tower = Earth_tower(self.x, self.y)
                tower_place.append((self.x // 48, self.y // 48))
                towers_group.add(tower)
                self.kill()
                gold -= 50
            elif xs - 24 < self.x and ys - 24 < self.y and gold >= 50:
                tower = Fire_tower(self.x, self.y)
                tower_place.append((self.x // 48, self.y // 48))
                towers_group.add(tower)
                self.kill()
                gold -= 50
            elif xs - 24 > self.x and ys - 24 < self.y and gold >= 50:
                tower = Storm_tower(self.x, self.y)
                tower_place.append((self.x // 48, self.y // 48))
                towers_group.add(tower)
                self.kill()
                gold -= 50


tile_images = {'grass': load_tiles('grass.png'), 'road_g': load_tiles('road_g.png'), 'road_v': load_tiles('road_v.png'),
               'road_1': load_tiles('road_1.png'), 'road_2': load_tiles('road_2.png'), 'road_3':
                   load_tiles('road_3.png'), 'road_4': load_tiles('road_4.png')}
tile_width = tile_height = 48

board = Board(10, 10)
generate_level(load_level('level_1.txt'))
# Spawn Enemies
# Координаты поворотов должны быть кратны скорости передвижения(5)
level_1 = [(0, 80), (335, 80), (335, 315), (240, 315), (240, 230), (0, 230)]

rect_group = pygame.sprite.Group()

timer_1 = time.time()
timer_2 = time.time()
clicks = 0
running = True
# Tower
tower_place = list()
tower_error = False

def start_screen():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if 157 < event.pos[0] < 322 and 165 < event.pos[1] < 191:
                    return
                if 157 < event.pos[0] < 322 and 288 < event.pos[1] < 314:
                    learn()
        pygame.display.flip()
        clock.tick(FPS)

start_screen()
while running:
    if HP == 0:
        defeat()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEMOTION:
            x, y = board.get_click(event.pos)
            full_x, full_y = event.pos[0], event.pos[1]
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # menu
                menu_group.update(full_x, full_y)
                # пытаемся удалить меню, если пользователь нажал мимо
                for elem in menu_group:
                    if not elem.rect.collidepoint(full_x, full_y):
                        elem.kill()
                if (x < 8 and y == 2) or (x == 7 and y == 3) or (x == 7 and y == 4) or \
                        ((x < 6 or x == 7) and y == 5) or ((x == 5 or x == 7) and y == 6) or \
                        ((4 < x < 8) and y == 7):
                    pass
                else:
                    if tower_place:
                        for elem in tower_place:
                            if elem[0] == x and elem[1] == y:
                                tower_error = True
                        if not tower_error:
                            if clicks == 0:
                                clicks += 1
                                timer_1 = time.time()
                            else:
                                clicks += 1
                                if time.time() - timer_1 < 0.3 and clicks == 2:
                                    menu = Select_menu(load_image('Select.png'), 1, 1, x * 48, y * 48)
                                    menu_group.add(menu)
                                    clicks = 0
                                else:
                                    clicks = 1
                                    timer_1 = time.time()
                        else:
                            tower_error = False
                    else:
                        if clicks == 0:
                            clicks += 1
                            timer_1 = time.time()
                        else:
                            clicks += 1
                            if time.time() - timer_1 < 0.3 and clicks == 2:
                                menu = Select_menu(load_image('Select.png'), 1, 1, x * 48, y * 48)
                                menu_group.add(menu)
                                clicks = 0
                            else:
                                clicks = 1
                                timer_1 = time.time()
    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    towers_group.draw(screen)
    enemies_group.draw(screen)
    projectiles_group.draw(screen)
    menu_group.draw(screen)
    rect_group.draw(screen)
    clock.tick(FPS)
    projectiles_group.update()
    enemies_group.update()
    towers_group.update()
    try:
        if (x < 8 and y == 2) or (x == 7 and y == 3) or (x == 7 and y == 4) or \
                ((x < 6 or x == 7) and y == 5) or ((x == 5 or x == 7) and y == 6) or \
                ((4 < x < 8) and y == 7) or (x, y) in tower_place:
            s = pygame.Surface((48, 48))
            s.set_alpha(128)
            s.fill((255, 0, 0))
            screen.blit(s, (x * 48, y * 48))
        else:
            s = pygame.Surface((48, 48))
            s.set_alpha(128)
            s.fill((0, 0, 255))
            screen.blit(s, (x * 48, y * 48))
    except BaseException:
        pass
    # Создаем врагов
    # Fire_Enemy(), Storm_Enemy(), Earth_Enemy(),
    enemy_list = [Water_Enemy()]
    if time.time() - timer_2 > 1:
        timer_2 = time.time()
        enemy = random.choice(enemy_list)
        enemies_group.add(enemy)

        for enemy in enemies_group:
            try:
                if enemy.reaction_reload:
                    print(time.time() - enemy.reaction_reload_timer)
                if time.time() - enemy.reaction_reload_timer > 1:
                    enemy.reaction_reload = False
                elif enemy.water_earth_reaction:
                    if time.time() - enemy.water_earth_reaction_timer > 0.5:
                        enemy.cycle += 1
                        enemy.HP -= 0.5
                        enemy.move_speed = 0.5
                if enemy.cycle == 3:
                    enemy.water_earth_reaction = False
            except BaseException:
                pass
    f1 = pygame.font.Font(None, 50)
    t1 = "gold: " + str(gold)
    text = f1.render(t1, True, (255, 255, 0))
    screen.blit(text, (10, 440))
    # display.flip должен быть последней командой
    pygame.display.flip()
terminate()
