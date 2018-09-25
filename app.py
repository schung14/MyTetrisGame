#!/usr/bin/env python3

import pygame, sys, math
from pygame.locals import *
from random import randrange as rand

pygame.init()

config = {
    'cell_size': 30,
    'rows': 20,
    'cols': 10,
    'border_width': 2,
    'game_state': 'starting',  # gamestates: 0 = starting, 1 = normal, 2 = paused, 3 = gameover
    'fps': 30,
    'delay': 1000,
    'd_repeat': 100,
    'num_players': None,
}

colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 150, 0),
    (0, 0, 255),
    (255, 120, 0),
    (255, 255, 0),
    (180, 0, 255),
    (0, 220, 220)
]

shapes = [
    [[1, 1, 0],
     [0, 1, 1]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 3],
     [0, 3, 0]],

    [[4, 4, 4],
     [4, 0, 0]],

    [[5, 5, 5],
     [0, 0, 5]],

    [[6, 6],
     [6, 6]],

    [[7, 7, 7, 7]]
]
display_width = 1280
display_height = 720
main_screen = pygame.display.set_mode((display_width, display_height))


def new_board():
    board = []
    for y in range(config['rows']):
        row = []
        for x in range(config['cols']):
            row.append(0)
        board.append(row)
    return board


def draw_matrix(surface, matrix, offx, offy, border_width):
    cs = config['cell_size']
    for cy, row in enumerate(matrix):
        for cx, val in enumerate(row):
            if val:
                pygame.draw.rect(surface, colors[val], (border_width + (offx + cx) * cs,
                                                        border_width + (offy + cy) * cs, cs, cs), 0)
                pygame.draw.rect(surface, colors[0], (border_width + (offx + cx) * cs,
                                                      border_width + (offy + cy) * cs, cs, cs), 1)


def rand_stone():
    return shapes[rand(len(shapes))]


def rotate_clockwise(shape):
    new_shape = []
    for x in range(len(shape[0])):
        new_row = []
        for y in range(len(shape) - 1, -1, -1):
            new_row.append(shape[y][x])
        new_shape.append(new_row)
    return new_shape


def rotate_counter_clockwise(shape):
    new_shape = []
    for x in range(len(shape[0]) - 1, -1, -1):
        new_row = []
        for y in range(len(shape)):
            new_row.append(shape[y][x])
        new_shape.append(new_row)
    return new_shape


def check_collision(board, shape, off_x, off_y):
    for cy, row in enumerate(shape):
        for cx, val in enumerate(row):
            try:
                if val and board[off_y + cy][off_x + cx]:
                    return True
            except IndexError:
                return True
    return False


def msg_center(msg, screen):
    for i, line in enumerate(msg.splitlines()):
        msg_image = pygame.font.Font(
            pygame.font.get_default_font(), 40).render(
            line, False, (255, 255, 255))

        msg_image_x, msg_image_y = msg_image.get_size()
        screen_x, screen_y = screen.get_size()
        screen.blit(msg_image, (
            (screen_x - msg_image_x) // 2,
            (screen_y - msg_image_y) // 2))


def quit():
    pygame.display.update()
    pygame.quit()
    sys.exit()


def start_button():
    if config['game_state'] == 'gameover':
        config['game_state'] = 'normal'
        run()
    elif config['game_state'] == 'normal':
        config['game_state'] = 'paused'
    elif config['game_state'] == 'paused':
        config['game_state'] = 'normal'
        main_screen.fill((0, 0, 0))


def set_speed(lines):
    threshold = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    delay = 1000
    for i in range(len(threshold)):
        if lines > threshold[i]:
            delay -= 95
    pygame.time.set_timer(USEREVENT + 1, delay)


def text_line(text):
    img = pygame.font.Font(pygame.font.get_default_font(), 20).render(text, False, (255, 255, 255))
    return img


def status_stone(stone):
    tmp_w = config['cell_size'] * 4 + config['border_width'] * 2
    tmp_h = config['cell_size'] * 3 + config['border_width'] * 2
    tmp_surface = pygame.Surface((tmp_w, tmp_h))
    pygame.draw.rect(tmp_surface, (255, 255, 255), (0, 0, tmp_w, tmp_h), config['border_width'])

    if stone:
        stone_w = len(stone[0]) * config['cell_size']
        stone_h = len(stone) * config['cell_size']
        stone_surface = pygame.Surface((stone_w, stone_h))
        draw_matrix(stone_surface, stone, 0, 0, 0)

        tmp_surface.blit(stone_surface, ((tmp_w - stone_w) // 2, (tmp_h - stone_h) // 2))

    return tmp_surface


def rand_lines(players):
    rcl1 = players[0].rand_line_counter
    rcl2 = players[1].rand_line_counter
    if rcl1 - rcl2 > 0:
        players[1].add_rand_lines(rcl1 - rcl2)
    elif rcl2 - rcl1 > 0:
        players[0].add_rand_lines(rcl2 - rcl1)
    for i, player in enumerate(players):
        player.rand_line_counter = 0


class StartMenu:
    pointer = pygame.font.Font(pygame.font.get_default_font(), 40).render("->", False, (255, 255, 255))

    items = [
        pygame.font.Font(pygame.font.get_default_font(), 40).render("1 Player", False, (255, 255, 255)),
        pygame.font.Font(pygame.font.get_default_font(), 40).render("2 Player", False, (255, 255, 255))
    ]
    buffer = 20

    menu_w = max(items[0].get_width(), items[1].get_width()) + pointer.get_width() + buffer * 2
    menu_h = (items[0].get_height() + 10) * len(items) + buffer * 2

    def __init__(self):
        self.menu = pygame.Surface((self.menu_w, self.menu_h))
        self.selected = 0
        self.update()

    def update(self):
        self.menu.fill((0, 0, 0))
        pygame.draw.rect(self.menu, (255, 255, 255), (0, 0, self.menu_w, self.menu_h), 1)
        y_pos = self.buffer
        x_pos = self.buffer + self.pointer.get_width()
        for item in self.items:
            self.menu.blit(item, (x_pos, y_pos))
            y_pos += item.get_height() + 10
        self.menu.blit(self.pointer, (self.buffer, self.buffer + self.selected * (self.pointer.get_height() + 10)))

    def move_pointer(self, val):
        self.selected -= val
        if self.selected > len(self.items) - 1:
            self.selected = 0
        elif self.selected < 0:
            self.selected = len(self.items) - 1
        self.update()

    def run_selected(self):
        config['num_players'] = self.selected + 1
        config['game_state'] = 'normal'
        run()


class PauseMenu:
    pointer = pygame.font.Font(pygame.font.get_default_font(), 40).render("->", False, (255, 255, 255))
    title = pygame.font.Font(pygame.font.get_default_font(), 40).render("Paused", False, (255, 255, 255))
    items = [
        pygame.font.Font(pygame.font.get_default_font(), 40).render("Resume", False, (255, 255, 255)),
        pygame.font.Font(pygame.font.get_default_font(), 40).render("Quit", False, (255, 255, 255))
    ]

    buffer = 20
    menu_w = max(items[0].get_width(), items[1].get_width()) + pointer.get_width() + buffer * 2
    menu_h = (items[0].get_height() + 10) * (len(items) + 1) + buffer * 2

    def __init__(self):
        self.menu = pygame.Surface((self.menu_w, self.menu_h))
        self.selected = 0
        self.update()

    def update(self):
        self.menu.fill((0, 0, 0))
        pygame.draw.rect(self.menu, (255, 255, 255), (0, 0, self.menu_w, self.menu_h), 2)
        y_pos = 0 + self.buffer
        x_pos = (self.menu_w - self.title.get_width()) // 2

        self.menu.blit(self.title, (x_pos, y_pos))

        y_pos += self.title.get_height() + 10
        x_pos = self.pointer.get_width() + self.buffer

        for item in self.items:
            self.menu.blit(item, (x_pos, y_pos))
            y_pos += item.get_height() + 10
        self.menu.blit(self.pointer, (self.buffer,
                                      self.buffer + (self.selected + 1) * (self.pointer.get_height() + 10)))

    def move_pointer(self, val):
        self.selected -= val
        if self.selected > len(self.items) - 1:
            self.selected = 0
        elif self.selected < 0:
            self.selected = len(self.items) - 1
        self.update()

    def run_selected(self):
        if self.selected == 0:
            config['game_state'] = 'normal'
        elif self.selected == 1:
            config['game_state'] = 'starting'
            run()


class Player:
    board_width = config['cell_size'] * config['cols']
    board_height = config['cell_size'] * config['rows']
    status_window_width = config['cell_size'] * 5
    border_width = config['border_width']

    def __init__(self, id_num):
        self.id_num = id_num
        self.screen = pygame.Surface((self.board_width + self.status_window_width + self.border_width * 2,
                                      self.board_height + self.border_width * 2))
        self.status = pygame.Surface((self.status_window_width, self.board_height))

        self.stone = None
        self.first_stone = rand_stone()
        self.second_stone = rand_stone()
        self.reserved_stone = None
        self.reserved = False

        self.board = new_board()
        self.stone_x = 0
        self.stone_y = 0
        self.new_stone()

        self.lines = 0
        self.score = 0

        self.rand_line_counter = 0

        self.controls = self.set_controls()

    def update_stats(self):
        self.status.fill((0, 0, 0))
        items = [
            text_line("Player " + str(self.id_num + 1)),
            text_line("Lines: " + str(self.lines)),
            text_line("Score: " + str(self.score)),
            text_line("Reserve"),
            status_stone(self.reserved_stone),
            text_line("Next"),
            status_stone(self.first_stone),
            status_stone(self.second_stone)
        ]

        y_pos = 10
        for each in items:
            ey = each.get_height()
            self.status.blit(each, (20, y_pos))
            y_pos += ey + 10

    def rotate_stone_cw(self):
        new_stone = rotate_clockwise(self.stone)
        if not check_collision(self.board, new_stone, self.stone_x, self.stone_y):
            self.stone = new_stone

    def rotate_stone_ccw(self):
        new_stone = rotate_counter_clockwise(self.stone)
        if not check_collision(self.board, new_stone, self.stone_x, self.stone_y):
            self.stone = new_stone

    def reserve_stone(self):
        if not self.reserved:
            if self.reserved_stone:
                temp = self.reserved_stone
                self.reserved_stone = self.stone
                self.stone = temp
            else:
                self.reserved_stone = self.stone
                self.new_stone()
            self.stone_x = (config['cols'] - len(self.stone[0])) // 2
            self.stone_y = 0
            self.reserved = True

    def new_stone(self):
        self.stone = self.first_stone
        self.first_stone = self.second_stone
        self.second_stone = rand_stone()

        self.stone_x = (config['cols'] - len(self.stone[0])) // 2
        self.stone_y = 0

        if check_collision(self.board, self.stone, self.stone_x, self.stone_y):
            config['game_state'] = 'gameover'

    def update_screen(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (255, 255, 255), (0, 0, self.board_width + self.border_width * 2,
                                                        self.board_height + self.border_width * 2), self.border_width)
        draw_matrix(self.screen, self.board, 0, 0, self.border_width)
        draw_matrix(self.screen, self.stone, self.stone_x, self.stone_y, self.border_width)
        self.update_stats()
        self.screen.blit(self.status, (self.board_width + self.border_width * 2, self.border_width))

    def merge(self):
        for cy, row in enumerate(self.stone):
            for cx, val in enumerate(row):
                if val:
                    self.board[self.stone_y + cy][self.stone_x + cx] = val

    def add_rand_lines(self, count):
        for i in range(count):
            new_row = []
            empty_spot = rand(config['cols'])
            for x in range(config['cols']):
                if x == empty_spot:
                    new_row.append(0)
                else:
                    new_row.append(rand(1, len(colors)))
            del (self.board[0])
            self.board += [new_row]

    def remove_lines(self):
        count = 0
        while True:
            for i, row in enumerate(self.board):
                if 0 not in row:
                    del (self.board[i])
                    self.score += 10 + count * 10
                    self.lines += 1
                    count += 1
                    new_row = []
                    for x in range(config['cols']):
                        new_row.append(0)
                    self.board = [new_row] + self.board
                    break
            else:
                break
        if count > 0:
            self.rand_line_counter = count - 1

    def drop(self):
        if config['game_state'] == 'normal':
            if check_collision(self.board, self.stone, self.stone_x, self.stone_y + 1):
                self.merge()
                self.new_stone()
                self.remove_lines()
                self.reserved = False
            else:
                self.stone_y += 1

    def drop_all(self):
        if config['game_state'] == 'normal':
            if check_collision(self.board, self.stone, self.stone_x, self.stone_y + 1):
                self.merge()
                self.new_stone()
                self.remove_lines()
                self.reserved = False
            else:
                self.stone_y += 1
                self.drop_all()

    def move(self, direction):
        new_x = self.stone_x + direction
        if new_x < 0:
            new_x = 0
        if new_x > config['cols'] - len(self.stone[0]):
            new_x = config['cols'] - len(self.stone[0])
        if not check_collision(self.board, self.stone, new_x, self.stone_y):
            self.stone_x = new_x

    def set_controls(self):
        controls = {
            'joy_button_actions': {
                0: self.rotate_stone_cw,      # A button
                1: self.rotate_stone_ccw,     # B button
                # 2: None,                    # X button
                # 3: None,                    # Y button
                4: self.reserve_stone,        # L1 button
                5: self.reserve_stone,        # R1 button
                # 6: None,                    # select button
                7: start_button               # start button
            },
            'joy_hat_actions': {
                'd_pad': (0, 0)
            },
            'joy_axis_actions': {
                0: 0,
                1: 0,
                'ready': True
            }
        }
        return controls

    def handle_event(self, event):
        if event.type == USEREVENT + 1:
            self.drop()
        elif event.type == pygame.JOYBUTTONDOWN:
            for key in self.controls['joy_button_actions']:
                if key == event.button:
                    self.controls['joy_button_actions'][event.button]()
        elif event.type == pygame.JOYHATMOTION:
            self.controls['joy_hat_actions'][0] = event.value
            if event.value[1] == 1:
                self.drop_all()
            elif event.value == (0, 0):
                pygame.time.set_timer(USEREVENT + 2 + self.id_num, 0)
            else:
                pygame.time.set_timer(USEREVENT + 2 + self.id_num, config['d_repeat'])
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                if abs(event.value) > 0.6:
                    self.controls['joy_axis_actions'][event.axis] = math.ceil(event.value)
                    pygame.time.set_timer(USEREVENT + 4 + self.id_num, config['d_repeat'])
                else:
                    self.controls['joy_axis_actions'][event.axis] = 0
            elif event.axis == 1:
                if event.value > 0.6:
                    self.controls['joy_axis_actions'][event.axis] = 1
                    pygame.time.set_timer(USEREVENT + 4 + self.id_num, config['d_repeat'])
                elif event.value < -0.6 and self.controls['joy_axis_actions']['ready']:
                    self.controls['joy_axis_actions'][event.axis] = -1
                    self.drop_all()
                    self.controls['joy_axis_actions']['ready'] = False
                elif abs(event.value) < 0.6:
                    self.controls['joy_axis_actions'][event.axis] = 0
                    self.controls['joy_axis_actions']['ready'] = True
        elif event.type == USEREVENT + 2 + self.id_num:
            if self.controls['joy_hat_actions'][0][0] != 0:
                self.move(self.controls['joy_hat_actions'][0][0])
            if self.controls['joy_hat_actions'][0][1] == -1:
                self.drop()
        elif event.type == USEREVENT + 4 + self.id_num:
            if self.controls['joy_axis_actions'][0] != 0:
                self.move(self.controls['joy_axis_actions'][0])
            if self.controls['joy_axis_actions'][1] == 1:
                self.drop()


def run():
    main_screen.fill((0, 0, 0))
    pygame.key.set_repeat(250, 100)
    pygame.event.set_blocked(MOUSEMOTION)

    fps_limit = pygame.time.Clock()

    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joysticks.append(pygame.joystick.Joystick(i).init())

    if config['game_state'] == 'starting':
        start_menu = StartMenu()
        menu_window = start_menu.menu

        key_actions = {
            'ESCAPE': quit,
            'DOWN': lambda: start_menu.move_pointer(1),
            'UP': lambda: start_menu.move_pointer(-1),
            'SPACE': start_menu.run_selected
        }

        while config['game_state'] == 'starting':
            start_w, start_h = menu_window.get_size()
            main_screen.blit(menu_window,
                             ((display_width - start_w) // 2,
                              (display_height - start_h) // 2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_" + key):
                            key_actions[key]()
                elif event.type == pygame.JOYHATMOTION:
                    start_menu.move_pointer(event.value[1])
                elif event.type == pygame.JOYAXISMOTION:
                    if event.axis == 1:
                        if abs(event.value) > 0.9:
                            start_menu.move_pointer(int(event.value))
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        start_menu.run_selected()

            fps_limit.tick(config['fps'])

    else:
        players = []
        for i in range(config['num_players']):
            players.append(Player(i))

        pause_menu = PauseMenu()

        pygame.time.set_timer(USEREVENT + 1, config['delay'])

        while True:
            if config['game_state'] == 'gameover':
                msg_center("GAME OVER!", main_screen)

            elif config['game_state'] == 'paused':
                pause_w, pause_h = pause_menu.menu.get_size()
                main_screen.blit(pause_menu.menu,
                                 ((display_width - pause_w) // 2,
                                  (display_height - pause_h) // 2))
                key_actions = {
                    'ESCAPE': quit,
                    'DOWN': lambda: pause_menu.move_pointer(1),
                    'UP': lambda: pause_menu.move_pointer(-1),
                    'SPACE': pause_menu.run_selected
                }
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()
                    elif event.type == pygame.KEYDOWN:
                        for key in key_actions:
                            if event.key == eval("pygame.K_" + key):
                                key_actions[key]()
                    elif event.type == pygame.JOYHATMOTION:
                        pause_menu.move_pointer(event.value[1])
                    elif event.type == pygame.JOYAXISMOTION:
                        if event.axis == 1:
                            if abs(event.value) > 0.9:
                                pause_menu.move_pointer(int(event.value))
                    elif event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 0:
                            pause_menu.run_selected()

            else: #gamestate = normal
                 key_actions = {
                    'ESCAPE': quit,
                    'LEFT': lambda: players[0].move(-1),
                    'RIGHT': lambda: players[0].move(+1),
                    'DOWN': players[0].drop,
                    'UP': players[0].rotate_stone_ccw,
                    'SPACE': start_button
                 }

                 for i, player in enumerate(players):
                    player.update_screen()
                    main_x = display_width // len(players)
                    player_x, player_y = player.screen.get_size()
                    main_screen.blit(player.screen, (
                        (main_x - player_x) // 2 + i * main_x,
                        (display_height - player_y) // 2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    for key in key_actions:
                        if event.key == eval("pygame.K_" + key):
                            key_actions[key]()
                elif event.type == pygame.JOYBUTTONDOWN:
                    players[event.joy].handle_event(event)
                elif event.type == pygame.JOYHATMOTION:
                    players[event.joy].handle_event(event)
                elif event.type == pygame.JOYAXISMOTION:
                    players[event.joy].handle_event(event)
                elif event.type == USEREVENT + 1:
                    if len(players) == 2:
                        rand_lines(players)
                    lines = 0
                    for i, player in enumerate(players):
                        player.handle_event(event)
                        lines += player.lines
                    set_speed(lines)
                else:
                     for i, player in enumerate(players):
                         player.handle_event(event)

            fps_limit.tick(config['fps'])


if __name__ == "__main__":
    run()
