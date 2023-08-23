from typing import List, Tuple

MAX_STEPS_EXCEEDED_REW = -1
MAX_REPEAT_MOVE_EXCEEDED_REW = -1

def get_reward(
        snake: List[Tuple[int]],
        food: Tuple[int],
        prev_snake: List[Tuple[int]],
        prev_food: Tuple[int],
        grid_size: Tuple[int],
        is_done: bool) -> float:

    # If game over, give negative reward
    if is_done:
        return -1

    prev_head = prev_snake[-1]
    new_head = snake[-1]

    # The snake has eaten an apple if it's new head position is the
    # same as the previous food position
    has_eaten = prev_food == new_head

    if has_eaten:
        return 1

    # To make the reward less sparse, give the agent positive reward
    # if it got closer to the food, negative if it got further away
    prev_dist = abs(food[0] - prev_head[0]) + abs(food[1] - prev_head[1])
    new_dist = abs(food[0] - new_head[0]) + abs(food[1] - new_head[1])
    rew = 0.1 if new_dist < prev_dist else -0.3

    return rew
