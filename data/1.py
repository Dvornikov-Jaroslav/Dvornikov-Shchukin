import os
import sys
import pygame
import time

pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 60
WIDTH = 480
HEIGHT = 480
timer = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
towers_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
menu_group = pygame.sprite.Group()
projectiles_group = pygame.sprite.Group()




def learn():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
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
    color_key = image.get_at((0, 0))
    if name != 'defeat.png' and name != 'fon.png' and name != 'fon1.png':
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
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

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

    def update(self, *args):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):
            if args[0].pos[0] - 24 > self.x and args[0].pos[1] - 24 > self.y:
                tower = Tower(load_image('water_tower1.png'), 23, 1, self.x, self.y) # Заменить на класс водной башни
                self.kill()
                towers_group.add(tower)
            if args[0].pos[0] - 24 < self.x and args[0].pos[1] - 24 > self.y:
                tower = Tower(load_image('earth_tower.png'), 8, 1, self.x, self.y)  # Заменить на класс земляной башни
                self.kill()
                towers_group.add(tower)
            if args[0].pos[0] - 24 < self.x and args[0].pos[1] - 24 < self.y:
                tower = Tower(load_image('fire_tower1.png'), 11, 1, self.x, self.y)  # Заменить на класс огненной башни
                self.kill()
                towers_group.add(tower)
            if args[0].pos[0] - 24 > self.x and args[0].pos[1] - 24 < self.y:
                tower = Tower(load_image('electro_tower.png'), 10, 1, self.x, self.y)  # Заменить на класс огненной башни
                self.kill()
                towers_group.add(tower)


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * self.width for _ in range(self.height)]

    def get_cell(self, mouse_pos):
        # получаем номер клетки
        x, y = mouse_pos
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
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.turn = 1
        self.win = False
        self.x, self.y = x / 48, y / 48
        self.HP = 2
        self.bullets = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.width * i, self.rect.height * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if len(enemies_group) == 0:
            pass
        elif (self.rect.x, self.rect.y) == level_1[5] and not self.win:
            self.rect.x = 0
            self.rect.y = 0
            self.kill()
            print(enemies_group)
            defeat()
            self.win = True
        elif not self.win:
            turn = level_1[self.turn - 1]
            next_turn = level_1[self.turn]
            if turn[0] < next_turn[0]:
                self.rect = self.rect.move(5, 0)
            elif turn[0] > next_turn[0]:
                self.rect = self.rect.move(-5, 0)
            elif turn[1] < next_turn[1]:
                self.rect = self.rect.move(0, 5)
            elif turn[1] > next_turn[1]:
                self.rect = self.rect.move(0, -5)
            if (self.rect.x, self.rect.y) == level_1[self.turn]:
                self.turn += 1
        else:
            pass
        # coords
        self.x, self.y = self.rect.x // 48 + 1, self.rect.y // 48 + 1
        if self.HP <= 0:
            self.kill()


class Fire_Enemy(Enemy):
    pass


class Storm_Enemy(Enemy):
    pass


class Earth_Enemy(Enemy):
    pass


class Water_Enemy(Enemy):
    pass


class Projectile(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, target):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.target = target
        self.x = x
        self.y = y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.width * i, self.rect.height * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        # moving
        x_dist = (self.target.rect.x - self.x) / 10
        y_dist = (self.target.rect.y - self.y) / 10
        self.rect = self.rect.move(x_dist, y_dist)
        collide = pygame.sprite.spritecollide(self, enemies_group, False)
        if collide:
            self.target.HP -= 1
            self.target.bullets -= 1
            self.kill()


class Tower(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.enemy_in_range = False
        self.x, self.y = x / 48, y / 48
        self.enemies_list = list()
        self.timer = time.time()
        self.timer_2 = time.time()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.width * i, self.rect.height * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        if time.time() - self.timer_2 > 0.15:
            self.timer_2 = time.time()
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
        # coords
        # для всех врагов
        for enemy in enemies_group:
            # в радиусе данной башни
            if ((enemy.x + 1 == self.x and enemy.y + 1 == self.y) or
                (enemy.x == self.x and enemy.y + 1 == self.y) or
                (enemy.x - 1 == self.x and enemy.y + 1 == self.y) or
                (enemy.x - 1 == self.x and enemy.y == self.y) or
                (enemy.x - 1 == self.x and enemy.y - 1 == self.y) or
                (enemy.x == self.x and enemy.y - 1 == self.y) or
                (enemy.x + 1 == self.x and enemy.y - 1 == self.y) or
                (enemy.x + 1 == self.x and enemy.y == self.y))\
                    and enemy.HP > 0 and enemy.HP - enemy.bullets > 0:
                # если враг до этого момента не был в радиусе башни, то добавляем и атакуем
                if enemy not in self.enemies_list:
                    self.enemies_list.append(enemy)
                else:
                    print(enemy, self.enemies_list[0])
                    if enemy == self.enemies_list[0]:
                        print('атака')
                        self.attack(enemy)
                    else:
                        print('Не тот враг!')
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
                if time.time() - self.timer > 1:
                    self.timer = time.time()
                    bullet = Projectile(load_image('fire_bullet.png'), 6, 1, self.rect.x, self.rect.y, enemy)
                    projectiles_group.add(bullet)
                    enemy.bullets += 1
            else:
                print("bullets don't attack")
        else:
            self.enemies_list.remove(enemy)



tile_images = {'grass': load_tiles('grass.png'), 'road_g': load_tiles('road_g.png'), 'road_v': load_tiles('road_v.png'),
               'road_1': load_tiles('road_1.png'), 'road_2': load_tiles('road_2.png'), 'road_3':
                   load_tiles('road_3.png'), 'road_4': load_tiles('road_4.png')}
tile_width = tile_height = 48

board = Board(10, 10)
generate_level(load_level('level_1.txt'))
# Spawn Enemies
# Координаты поворотов должны быть кратны скорости передвижения(5)
level_1 = [(0, 85), (335, 85), (335, 320), (235, 320), (235, 230), (0, 230)]




def main():

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = board.get_click(event.pos)
                if event.button == 1:
                    menu_group.update(event)
                    fire_enemy = Fire_Enemy(load_image('fire_enemy.png'), 4, 1, level_1[0][0], level_1[0][1])
                    enemies_group.add(fire_enemy)
                elif event.button == 3:
                    storm_enemy = Storm_Enemy(load_image('storm_enemy.png'), 4, 1, level_1[0][0], level_1[0][1])
                    enemies_group.add(storm_enemy)
                elif event.button == 4:
                    earth_enemy = Earth_Enemy(load_image('earth_enemy.png'), 4, 1, level_1[0][0], level_1[0][1])
                    enemies_group.add(earth_enemy)
                elif event.button == 5:
                    water_enemy = Water_Enemy(load_image('water_enemy.png'), 4, 1, level_1[0][0], level_1[0][1])
                    enemies_group.add(water_enemy)
                elif event.button == 2:
                    x, y = board.get_click(event.pos)
                    menu = Select_menu(load_image('Select.png'), 1, 1, x * 48, y * 48)
                    menu_group.add(menu)
                    print(x, y)
                    if (x < 8 and y == 2) or (x == 7 and y == 3) or (x == 7 and y == 4) or \
                            ((x < 6 or x == 7) and y == 5) or ((x == 5 or x == 7) and y == 6) or \
                            ((4 < x < 8) and y == 7):
                        pass
        screen.fill(pygame.Color(0, 0, 0))
        tiles_group.draw(screen)
        towers_group.draw(screen)
        enemies_group.draw(screen)
        menu_group.draw(screen)
        projectiles_group.draw(screen)
        pygame.display.flip()
        clock.tick(7)
        all_sprites.update()
        projectiles_group.update()


    terminate()


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
                    main()
                    return
                if 157 < event.pos[0] < 322 and 288 < event.pos[1] < 314:
                    learn()
        pygame.display.flip()
        clock.tick(FPS)

start_screen()