import sys
import numpy as np
from random import randint  # из набора инструментов для создания рандомных чисел берем инструмент для рандомного int

import pygame as pg  # берем инструмент pygame и называем его pg для удобства


class GameLogic:
    def __init__(self, app, max_score=0):
        self.app = app
        self.field_width = self.app.screen.get_width() // 60  # устанавливаем ширину карты
        self.field_height = self.app.screen.get_height() // 60  # устанавливаем высоту карты
        self.field = [[0] * self.field_height for _ in range(self.field_width)]
        self.figure = []
        self.figure_type = 0
        self.figure_dir = 0
        self.create_figure()
        self.game_over = False
        self.game_paused = False
        self.timer = 0
        self.score = 0
        self.max_score = max_score

    def create_figure(self):
        self.figure_type = randint(0, 6)
        self.figure_dir = 0
        x = self.field_width // 2 - 1
        y = 0
        if self.figure_type == 0:  # Квадрат
            self.figure = [[x, y], [x + 1, y], [x, y + 1], [x + 1, y + 1]]
        if self.figure_type == 1:  # Палка
            self.figure = [[x, y], [x, y + 1], [x, y + 2], [x, y + 3]]
        if self.figure_type == 2:  # Палка с хвостом вправо
            self.figure = [[x, y], [x, y + 1], [x, y + 2], [x + 1, y + 2]]
        if self.figure_type == 3:  # Палка с хвостом влево
            self.figure = [[x, y], [x, y + 1], [x, y + 2], [x - 1, y + 2]]
        if self.figure_type == 4:  # Фигура в форме отраженной "Z"
            self.figure = [[x + 1, y], [x, y], [x, y + 1], [x - 1, y + 1]]
        if self.figure_type == 5:  # Фигура в форме "Z"
            self.figure = [[x, y], [x + 1, y], [x + 1, y + 1], [x + 2, y + 1]]
        if self.figure_type == 6:  # Фигура в форме "T"
            self.figure = [[x, y], [x + 1, y], [x + 2, y], [x + 1, y + 1]]

    def restart(self):
        self.field = [[0] * self.field_height for _ in range(self.field_width)]
        self.field = [[0] * self.field_height for _ in range(self.field_width)]
        self.figure = []
        self.create_figure()
        self.game_over = False
        self.game_paused = False
        self.timer = 0
        self.score = 0
        print(f'Max score is {self.max_score}!')

    def update(self):
        if self.game_over:
            return

        if self.game_paused:
            return

        self.timer += self.app.dt

        delay = 0.3
        if self.timer < delay:
            return
        self.timer -= delay

        for i in range(self.field_width):
            if self.field[i][0] == 1:
                self.game_over = True
                if self.score > self.max_score:
                    self.max_score = self.score

        new_figure = []
        for i in range(len(self.figure)):
            new_figure.append(self.figure[i].copy())
        for i in range(len(new_figure)):
            new_figure[i][1] = new_figure[i][1] + 1

        max_y = new_figure[0][1]
        for i in range(len(new_figure)):
            if new_figure[i][1] > max_y:
                max_y = new_figure[i][1]
        if max_y == self.field_height - 1:  # обработка касания пола
            for i in range(len(new_figure)):
                x = new_figure[i][0]
                y = new_figure[i][1]
                self.field[x][y] = 1
            self.create_figure()
            return
        for i in range(len(new_figure)):  # обработка касания блоков
            x = new_figure[i][0]
            y = new_figure[i][1]
            if self.field[x][y] == 1:  # or self.field[x][max_y] - не сработал
                for j in range(len(self.figure)):
                    x1 = self.figure[j][0]
                    y1 = self.figure[j][1]
                    self.field[x1][y1] = 1
                self.create_figure()
                return

        for i in range(self.field_height):  # обработка заполнения полосы
            is_full = True
            for j in range(self.field_width):
                if self.field[j][i] != 1:
                    is_full = False
            if is_full:
                for j in range(self.field_width):
                    self.field[j][i] = 0
                for i1 in range(i, 0, -1):
                    for j1 in range(0, self.field_width):
                        self.field[j1][i1] = self.field[j1][i1 - 1]
                self.score += 1

        self.figure = new_figure

    def draw(self):
        self.draw_figure()
        self.draw_building()
        self.drawGrid()
        self.draw_score()
        if self.game_over:
            self.draw_game_over()
        if self.game_paused:
            self.draw_game_paused()

    def draw_game_over(self):  # метод прорисовки заставки "Игра окончена"
        img = self.app.score_font.render(f'You lose scoring {self.score}. Max record is {self.max_score}', True,
                                         (255, 0, 0))
        self.app.screen.blit(img, (170, 400))

    def draw_game_paused(self):
        img = self.app.score_font.render('Pause', True, (255, 0, 0))
        self.app.screen.blit(img, (270, 400))

    def draw_score(self):  # метод прорисовки очков
        img = self.app.score_font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.app.screen.blit(img, (20, 20))

    def draw_figure(self):
        for index, square in enumerate(self.figure):
            pg.draw.rect(self.app.screen, (0, 255, 255), [square[0] * 60, square[1] * 60, 60, 60])

    def draw_building(self):
        for x in range(self.field_width):
            for y in range(self.field_height):
                if self.field[x][y] == 1:
                    pg.draw.rect(self.app.screen, (0, 255, 0), [x * 60, y * 60, 60, 60])

    def drawGrid(self):
        for x in range(self.field_width):
            for y in range(self.field_height):
                pg.draw.rect(self.app.screen, (30, 30, 30), [x * 60, y * 60, 60, 60], 1)

    def move_left(self):
        new_figure = []
        for i in range(len(self.figure)):
            new_figure.append(self.figure[i].copy())
        min_x = new_figure[0][0]
        for i in range(len(new_figure)):
            if new_figure[i][0] < min_x:
                min_x = new_figure[i][0]
        if min_x > 0:
            for i in range(len(new_figure)):
                new_figure[i][0] -= 1
        for i in new_figure:
            x = i[0]
            y = i[1]
            if self.field[x][y] == 1:
                return
        self.figure = new_figure

    def move_right(self):
        new_figure = []
        for i in range(len(self.figure)):
            new_figure.append(self.figure[i].copy())
        max_x = new_figure[0][0]
        for i in range(len(new_figure)):
            if new_figure[i][0] > max_x:
                max_x = new_figure[i][0]
        if max_x < self.field_width - 1:
            for i in range(len(new_figure)):
                new_figure[i][0] += 1
        for i in new_figure:
            x = i[0]
            y = i[1]
            if self.field[x][y] == 1:
                return
        self.figure = new_figure

    def rot_l(self):
        self.figure_dir += 1
        if self.figure_dir == 4:
            self.figure_dir = 0
        if self.figure_type == 1:
            self.rot_stick()
        elif self.figure_type > 1:
            figure_matrix = [[0] * 3 for _ in range(3)]
            x = self.figure[1][0] - 1
            y = self.figure[1][1] - 1
            for i in range(len(self.figure)):  # записали фигуру в матрицу
                figure_matrix[self.figure[i][0] - x][self.figure[i][1] - y] = 1
            figure_matrix = np.rot90(figure_matrix, k=3)  # повернули
            self.figure = []
            need_first_coord = True
            for i in range(len(figure_matrix)):
                for j in range(len(figure_matrix[0])):
                    if i != j and figure_matrix[i][j] == 1 and need_first_coord:
                        first_coord = [x + i, y + j]  # записали первую координату
                        self.figure.append(first_coord)
                        need_first_coord = False
            second_coord = [x + 1, y + 1]
            self.figure.append(second_coord)
            for i in range(len(figure_matrix)):
                for j in range(len(figure_matrix[0])):
                    if figure_matrix[i][j] == 1 and not [i + x, j + y] in self.figure:
                        coord = [i + x, j + y]
                        self.figure.append(coord)

    def rot_r(self):
        self.figure_dir -= 1
        if self.figure_dir == -1:
            self.figure_dir = 3
        if self.figure_type == 1:
            self.rot_stick()
        elif self.figure_type > 1:
            figure_matrix = [[0] * 3 for _ in range(3)]
            x = self.figure[1][0] - 1
            y = self.figure[1][1] - 1
            for i in range(len(self.figure)):  # записали фигуру в матрицу
                figure_matrix[self.figure[i][0] - x][self.figure[i][1] - y] = 1
            figure_matrix = np.rot90(figure_matrix)  # повернули
            self.figure = []
            need_first_coord = True
            for i in range(len(figure_matrix)):
                for j in range(len(figure_matrix[0])):
                    if i != j and figure_matrix[i][j] == 1 and need_first_coord:
                        first_coord = [x + i, y + j]  # записали первую координату
                        self.figure.append(first_coord)
                        need_first_coord = False
            second_coord = [x + 1, y + 1]
            self.figure.append(second_coord)
            for i in range(len(figure_matrix)):
                for j in range(len(figure_matrix[0])):
                    if figure_matrix[i][j] == 1 and not [i + x, j + y] in self.figure:
                        coord = [i + x, j + y]
                        self.figure.append(coord)

    def rot_stick(self):
        if self.figure_type == 1:  # Палка
            if self.figure_dir % 2 == 1:  # Повернули горизонтально
                x = self.figure[0][0]
                y = self.figure[0][1]
                self.figure = [[x - 2, y + 2], [x - 1, y + 2], [x, y + 2], [x + 1, y + 2]]
            else:  # Повернули вертикально
                x = self.figure[0][0]
                y = self.figure[0][1]
                self.figure = [[x + 2, y - 2], [x + 2, y - 1], [x + 2, y], [x + 2, y + 1]]


class App:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((600, 960))
        pg.display.set_caption('Tetris')
        print(type(self.screen))
        self.clock = pg.time.Clock()
        self.score_font = pg.font.SysFont("exo2extrabold", 24)
        self.dt = 0.0
        self.logic = GameLogic(self)

    def check_events(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                if self.logic.game_paused:
                    self.logic.game_paused = False
                else:
                    self.logic.game_paused = True
            if self.logic.game_over:
                if e.type == pg.KEYDOWN:
                    self.logic.restart()
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_LEFT or e.key == ord('a'):
                    self.logic.move_left()
                if e.key == pg.K_RIGHT or e.key == ord('d'):
                    self.logic.move_right()
                if e.key == ord('q'):
                    self.logic.rot_l()
                if e.key == ord('e'):
                    self.logic.rot_r()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.logic.draw()

    def update(self):
        self.logic.update()
        pg.display.flip()
        self.dt = self.clock.tick() * 0.001

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()


app = App()
app.run()
