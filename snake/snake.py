# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 16:25:20 2018

@author: houlu
"""
import sys
import random
import itertools
import numpy as np
from collections.abc import Sequence


class Snake(Sequence):

    UP = (-1, 0)
    DOWN = (1, 0)
    RIGHT = (0, 1)
    LEFT = (0, -1)
    INITIAL_POS = [(1, 4), (1, 3), (1, 2), (1, 1)]

    def __init__(self):
        self.all_directions = [self.LEFT, self.RIGHT, self.UP, self.DOWN]
        self.dir_names = ['left', 'right', 'up', 'down']
        self.dir2names = dict(zip(self.all_directions, self.dir_names))
        self.dirnumber = len(self.all_directions)
        self.action_to_direction = dict(enumerate(self.all_directions))

    def __getitem__(self, item):
        return self.pos[item]

    def __len__(self):
        return len(self.pos)

    def __iter__(self):
        return iter(self.pos)

    def __contains__(self, item):
        return item in self.pos

    @staticmethod
    def _tuple_add(t1, t2):
        return t1[0] + t2[0], t1[1] + t2[1]

    @property
    def occupation(self):
        return set(self)

    @property
    def inversion(self):
        return -self.direction[0], -self.direction[1]

    def move(self):
        self.pos.insert(0, self._tuple_add(self.head, self.direction))
        self.pos.pop(-1)
        self.head = self[0]

    def turn(self, action_index):
        if action_index is None:
            return
        try:
            next_direction = self.action_to_direction[action_index]
        except KeyError:
            return
        if next_direction == self.inversion:
            return
        else:
            self.direction = next_direction

    def eat(self, food):
        if self.head == food:
            self.pos.append(self.pos[-1])
            return True
        else:
            return False

    @property
    def available_directions(self):
        return [ind
                for ind, action in enumerate(self.all_directions)
                if not (self._tuple_add(self.head, action) == self[1])
        ]

    def reset(self):
        self.pos = self.INITIAL_POS[:]
        self.head = self[0]
        self.direction = self.RIGHT


class Food:

    def __init__(self):
        self.color = (52, 115, 243)

    @staticmethod
    def _gen(allowed):
        return random.choice(allowed)

    def replenish(self, allowed):
        self.pos = self._gen(allowed)


class Game:

    def __init__(self, number, window=None):
        self.number = number
        self.window = window
        self.state_number = self.number + 2
        self.boundry = (1, self.number + 1)
        self.shape = (self.state_number, self.state_number)
        self.grid = set(itertools.product(range(*self.boundry), range(*self.boundry)))
        self.value = {
            'head': 1,
            'body': -1,
            'food': 2,
            'wall': -2,
            'earth': 0
        }

        self._state = np.zeros(self.shape)
        self.snake = Snake()
        self.food = Food()
        self.reset()

        self.score = 0

    @property
    def allowed(self):
        return list(self.grid - self.snake.occupation)

    @property
    def actions(self):
        return self.snake.available_directions

    @property
    def state(self):
        self._state[1:self.number + 1, 1:self.number + 1] = self.value['earth']
        self._state[self.food.pos[0], self.food.pos[1]] = self.value['food']
        for body in self.snake:
            self._state[body[0], body[1]] = self.value['body']
        self._state[self.snake.head[0], self.snake.head[1]] = self.value['head']
        return self._state

    def observation(self):
        return self.state.reshape((self.number + 2, self.number + 2, 1), order='F')

    @property
    def eat(self):
        return self.snake.eat(self.food.pos)

    @property
    def size(self):
        return self.state_number, self.snake.dirnumber

    @property
    def info(self):
        info = 'Score: {}'.format(self.score)
        return info

    @property
    def death(self):
        body = self.snake[1:]
        if self.snake.head in body:
            return True
        if (not self.boundry[0] <= self.snake.head[0] < self.boundry[1])\
                or (not self.boundry[0] <= self.snake.head[1] < self.boundry[1]):
            return True
        return False

    def step(self, action):
        self.snake.turn(action)
        self.snake.move()
        death = self.death
        if self.eat:
            self.new_food()
        return self.observation(), self.reward(death), death, self.info

    def render(self):
        if self.window is not None:
            self.window.draw(self.state)

    def reset(self):
        self.snake.reset()
        self.food.replenish(self.allowed)
        self._state[[0, self.number + 1], :] = self.value['wall']
        self._state[:, [0, self.number + 1]] = self.value['wall']

    def new_food(self):
        self.score += 1
        self.food.replenish(self.allowed)

    def reward(self, death):
        if self.eat:
            return 10
        elif death:
            return -10
        else:
            return 0

    def play(self, policy=None):
        self.render()
        state = self.observation()
        while True:
            if policy is not None:
                action_index = policy(state)
                if action_index is False:
                    return
            else:
                action_index = self.snake.direction
            state, reward, terminal, info = self.step(action_index)
            print(info)
            self.render()
            if self.death:
                return

    def close(self):
        try:
            self.window.close()
        except AttributeError:
            del self.window


if __name__ == '__main__':
    base_size = 20
    expansion = 1.5
    number = 10
    from window import Window
    window = Window(number=number, block_size=base_size, expansion=expansion, speed=0.1)
    g = Game(number=number, window=window)
    g.play()
    sys.exit(0)
