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
timer = 0

player = None
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

    if color_key == -1:
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
    image = load_image("Fire_1.gif")
    def __init__(self, x, y):
        super().__init__(towers_group, all_sprites)
        self.image = Tower.image
        self.rect = self.image.get_rect().move(x, y)




tile_images = {'grass': load_image('grass.png'), 'road_g': load_image('road_g.png'), 'road_v': load_image('road_v.png'),
               'road_1': load_image('road_1.png'), 'road_2': load_image('road_2.png'), 'road_3':
                   load_image('road_3.png'), 'road_4': load_image('road_4.png')}
tile_width = tile_height = 48

generate_level(load_level('level_1.txt'))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if timer == 0:
                    timer = 0.001
                elif timer < 0.5:
                    print(all_sprites)
                    Tower(pygame.mouse.get_pos()[0] // 48 * 48, pygame.mouse.get_pos()[1] // 48 * 48)
                    timer = 0
    screen.fill(pygame.Color(0, 0, 0))
    tiles_group.draw(screen)
    towers_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

terminate()