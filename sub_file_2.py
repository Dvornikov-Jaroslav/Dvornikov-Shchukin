import os
import sys
import pygame

pygame.init()
pygame.key.set_repeat(200, 70)

FPS = 60
WIDTH = 480
HEIGHT = 480

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
towers_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()


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


class Tower(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

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


class Enemy(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(enemies_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.turn = 1
        self.win = False

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
        if (self.rect.x, self.rect.y) == level_1[5] and not self.win:
            enemies_group.remove(fire_enemy)
            print('вы проиграли')
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


class Fire_Enemy(Enemy):
    pass


class Storm_Enemy(Enemy):
    pass


class Earth_Enemy(Enemy):
    pass


class Water_Enemy(Enemy):
    pass


tile_images = {'grass': load_tiles('grass.png'), 'road_g': load_tiles('road_g.png'), 'road_v': load_tiles('road_v.png'),
               'road_1': load_tiles('road_1.png'), 'road_2': load_tiles('road_2.png'), 'road_3':
                   load_tiles('road_3.png'), 'road_4': load_tiles('road_4.png')}
tile_width = tile_height = 48

board = Board(10, 10)
generate_level(load_level('level_1.txt'))
# Spawn Enemies
# Координаты поворотов должны быть кратны скорости передвижения(5)
level_1 = [(0, 85), (335, 85), (335, 320), (235, 320), (235, 230), (0, 230)]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = board.get_click(event.pos)
            if event.button == 1:
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
    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    towers_group.draw(screen)
    enemies_group.draw(screen)
    pygame.display.flip()
    clock.tick(7)
    all_sprites.update()

terminate()