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


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key == -1 or name == 'fire_tower.png':
        color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
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


tile_images = {'grass': load_image('grass.png'), 'road_g': load_image('road_g.png'), 'road_v': load_image('road_v.png'),
               'road_1': load_image('road_1.png'), 'road_2': load_image('road_2.png'), 'road_3':
                   load_image('road_3.png'), 'road_4': load_image('road_4.png')}
tile_width = tile_height = 48

board = Board(10, 10)
generate_level(load_level('level_1.txt'))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = board.get_click(event.pos)
            fire_tower = Tower(load_image('fire_tower.png'), 6, 1, (x - 1) * 48, (y - 1) * 48)
            all_sprites.add(fire_tower)
    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(10)
    all_sprites.update()

terminate()