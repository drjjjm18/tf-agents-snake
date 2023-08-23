import matplotlib.pyplot as plt
from environment import SnakeEnvironment


env = SnakeEnvironment()
env.reset()
snake_img = env.render()
start_snake_l = len(env._snake)

fig, ax = plt.subplots(1, 1)
img = ax.imshow(snake_img)
action_dict = {'left': 3, 'up': 0, 'right': 1, 'down': 2}

action = {'val': 1}

fig.canvas.mpl_connect('key_press_event', lambda e:
                       action.__setitem__('val', action_dict[e.key]))

is_over = None
while not is_over:
    img.set_data(snake_img)
    fig.canvas.draw_idle()
    plt.pause(0.1)
    obs, rew, is_over, _ = env.step(action['val'])
    snake_img = env.render()

print('Score:', len(env._snake) - start_snake_l)
