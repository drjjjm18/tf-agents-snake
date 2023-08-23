from argparse import ArgumentParser
import time
import os

import cv2
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

from environment import SnakeEnvironment
from user_eval_fn import init, agent_predict


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument('modelpath')
    parser.add_argument('-n', '--num-episodes', default=5, type=int)
    args = parser.parse_args()

    init(args.modelpath)
    env = SnakeEnvironment()

    for i in range(args.num_episodes):
        obs = env.reset()
        is_done = False
        img = cv2.resize(env.render(), (480, 480), interpolation = cv2.INTER_AREA)
        cv2.imshow('Watch Snake', img)
        cv2.setWindowProperty('Watch Snake', cv2.WND_PROP_TOPMOST, 1)

        while not is_done:
            cv2.waitKey(1)
            time.sleep(0.05)
            action = agent_predict(obs)
            obs, rew, is_done, _ = env.step(action)
            img = cv2.resize(env.render(), (480, 480), interpolation = cv2.INTER_AREA)
            cv2.imshow('Watch Snake', img)
