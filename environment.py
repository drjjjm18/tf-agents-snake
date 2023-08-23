from typing import Tuple, List
import random
import numpy as np

from gym import Env
from gym.spaces import Discrete

from user_rew_fn import MAX_REPEAT_MOVE_EXCEEDED_REW, MAX_STEPS_EXCEEDED_REW, get_reward
from user_obs_fn import get_observation, observation_space
from utils import tuple_sum, tuple_diff


def random_food_position(grid_size, snake):
    # Sample new food position
    possible_pos = {(a, b) for a in range(grid_size[0]) for b in range(grid_size[1])}
    # Remove unavailable positions
    for sp in snake:
        possible_pos.remove(sp)
    return random.choice(list(possible_pos))


def update(grid_size: Tuple[int], snake: List[Tuple[int]], food: Tuple[int], action: int):
    # Return (snake, food, is_over)
    # NOTE: might be easier for algorithm to get as action an absolute direction, rather than relative to snake current dir
    # First index is heigh, second is width. Origin is top left of grid
    # In snake list, last tuple is head position

    dir = tuple_diff(snake[-1], snake[-2])
    new_dir = [
        [-1, 0],
        [0, 1],
        [1, 0],
        [0, -1]
    ][action]
    # If action is opposite of current direction, then do nothing
    if tuple_sum(dir, new_dir) == (0, 0):
        new_dir = dir
    next_pos = tuple_sum(snake[-1], new_dir)

    # If snake hit wall or itself
    if (not 0 <= next_pos[0] < grid_size[0]) or (not 0 <= next_pos[1] < grid_size[1]) or next_pos in snake:
        return snake, food, True

    # Add new block to snake
    snake.append(next_pos)

    # If snake hit food
    if next_pos == food:
        food = random_food_position(grid_size, snake)
    else:
        # If snake just moved forward without hitting anything
        snake = snake[1:]

    return snake, food, False

    

class SnakeEnvironment(Env):

    def __init__(self):
        self.action_space = Discrete(4)
        self.observation_space = observation_space()

        self._grid_size = (24, 24)
        self._init_snake = [(0, 1), (0, 2)]
        self._food = (12, 12)
        self._episode_ended = False
        self.steps = 0
        self.repeated_move_check = []

    def render(self, mode='rgb_array'):
        if mode == 'rgb_array':
            img = np.full((*self._grid_size, 3), 255, np.uint8)
            img[tuple(zip(*self._snake))] = [0, 0, 255]
            img[self._snake[-1]] = [0, 255, 0]
            img[self._food] = [255, 0, 0]
            return img
        else:
            raise NotImplementedError(f"Rendering mode '{mode}' has not been implemented")

    def reset(self):
        self._snake = self._init_snake[:]
        self._prev_snake = None
        self._food = random_food_position(self._grid_size, self._snake)
        self._prev_food = None
        self._episode_ended = False
        self.steps = 0
        self.repeated_move_check = []
        observation = get_observation(self._snake, self._food, self._prev_snake, self._prev_food, self._grid_size)
        return observation

    def step(self, action):
        self.steps += 1
        
        if action in self.repeated_move_check:
            self.repeated_move_check.append(action)
        else:
            self.repeated_move_check = [action]
            
        if self.steps >= 2000:
            observation = get_observation(self._snake, self._food, self._prev_snake, self._prev_food, self._grid_size)
            return observation, MAX_STEPS_EXCEEDED_REW, True, {}

        if len(self.repeated_move_check) > 25:
            observation = get_observation(self._snake, self._food, self._prev_snake, self._prev_food, self._grid_size)
            return observation, MAX_REPEAT_MOVE_EXCEEDED_REW, True, {}

        self._prev_snake = self._snake[:]
        self._prev_food = self._food
        snake, food, is_done = update(self._grid_size, self._snake, self._food, action)
        self._snake = snake
        self._food = food

        # Reward calculations
        reward = get_reward(self._snake, self._food, self._prev_snake, self._prev_food, self._grid_size, is_done)
        observation = get_observation(self._snake, self._food, self._prev_snake, self._prev_food, self._grid_size)

        return observation, reward, is_done, {}

    @property
    def current_score(self):
        return len(self._snake) - len(self._init_snake)
