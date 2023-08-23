# A reinforcement learning environment for a classic Snake style game

This repository is the starting point for the RL hackathon. It contains a pre-built snake enviornment which can be used to experiment with tf-agents and reinforcement learning (RL). Here you can:
* play snake on your computer
* train an agent to play snake
* watch an agent playing snake

<img src="images/nokia-snake-game.gif">

- [A reinforcement learning environment for a classic Snake style game](#a-reinforcement-learning-environment-for-a-classic-snake-style-game)
  - [Set up](#set-up)
    - [Code](#code)
    - [Submission account](#submission-account)
  - [Usage](#usage)
  - [The game](#the-game)
  - [The RL environment](#the-rl-environment)
  - [The RL agent](#the-rl-agent)
  - [The Challenge and submission process](#the-challenge-and-submission-process)
    - [Limits](#limits)

## Set up

### Code

First clone the repo. In a terminal, use the following commands:
```
# change directory to the folder you want to clone repo in, e.g. Documents/code shown below
cd Documents/code
# Use HTTPS or SSH 
git clone https://github.com/danalyticsuk/pavlovs-snake.git
# git clone git@github.com:danalyticsuk/pavlovs-snake.git
cd pavlovs-snake
```

Next make sure you have the dependencies installed. You'll need python 3 (we have tested it on python 3.9.7 on MacOS), and pytorch, tensorflow and tf-agents installed. You can use requirements.txt to make sure you have the right versions:

**Optional** Consider creating a virtual environment:
```
# create python venv
python -m venv snake_env
# activate venv - note this varies between windows, bash and mac
snake_env\Scripts\activate # linux/bash terminal: source snake_env/Scripts/activate # mac: source snake_env/bin/activate
```

Install dependencies:
```
python -m pip install -r requirements.txt
```

### Submission account

In order to make a submission you will require some AWS credentials that we will generate for you on the day of the challenge. To set them please follow the [documentation here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html). We recommend either setting environment variables or creating a shared credential file among those options. If you are unsure how to do that in your environment, have a look on Google or speak with a member of the Hackathon support team.

## Usage

To run the training for the RL algorithm run:

```bash
python user_train.py model/
```

To watch the trained model play the game run:

```bash
python watch_agent.py model/
```

To evaluate model performance over many games and return other metrics, run:

```bash
python evaluate_agent.py model/
```

Once you are happy about your performance and you want to submit your agent (this will submit the `user_*` files and the whole `model/` folder):

```bash
python make_submission.py <your-team-name>
```

After some time that you made your submission, if you want to check the logs from it (in case it did not show up on the leaderboard):

```bash
python check_submission_logs.py <your-team-name> <submission-filename>
```

## The game

The game is the traditional Snake 1 game from old phones, where travelling through walls was not possible (the snake dies when crashing into the wall). You are controlling a snake slithering through the screen, and the objective is to eat as many apples (red squares) without crashing into the snake's tail or the walls. Every apple you eat, your score goes up by 1 and the snake's tail grows by 1 block.

You will be creating a reinforcement learning agent to learn to play the game by interacting with it. To test the game for yourself, run the `play_game.py` script, and using the arrow keys to control the snake. Note that to be able to play the game you will need to `pip install matplotlib`.

The game is implemented as the `update(...)` function in the `environment.py` file. You will not have to directly update the game or the environment yourself (those files will be ignored for the submission), but feel free to read through it and play with it.


## The RL environment

As mentioned above, the RL environment is implemented in `environment.py`, and it is a wrapper to the basic game logic. It is implemented (loosely) following the [OpenAI Gym specification](https://www.gymlibrary.dev/api/core/), a standard for reinforcement learning research. Please refer to the linked documentation to understand the basic API.

As in all reinforcement learning, we will work with observations, actions and rewards to get our agent to learn how play the game. The action, chosen at each time step, is fixed, and it is an integer from 0 to 3 included indicating which direction the snake should be turning. If the current direction of movement (or the opposite one) is chosen, the snake will not change direction.

You will be able to update the functions that generate the current agent observation and the reward, used by the environment, to improve the agent's learning. They are declared in the `user_obs_fn.py` and `user_rew_fn.py` files (please do not change the arguments to the function or the number of returned elements).

The observation function `get_observation(...)` in `user_obs_fn.py` is used by the environment and it determines what the agent will "see" at every interaction with the environment. In the provided working sample, this will be in the format of a python list, where each element is a numerical value representing some information about the environment. Given this is fed to a neural network, make sure each of the numbers in the observation are close to the `[-1, 1]` and the size of their range does not vary too drastically from one to another.

**NOTE:** If you are planning to change the length or the format returned by the observation function, make sure to update the `observation_space()` function as well to return the [appropriate Gym Space](https://www.gymlibrary.dev/api/spaces/). Also be aware that if you move away from a 1D input, you will also have to update the agent's network to accommodate for it.

The reward function `get_reward(...)` in `user_rew_fn.py` is used by the environment and it determines what reward the agent will get at each timestep. The returned value should be a scalar number, which is positive when the agent did something good and negative when the agent did something bad.

**NOTE:** At evaluation time your reward function will be ignored and we will use some form of reward mainly based on the number of apples eaten at the end of the game.

The inputs to these methods are as such:
```
snake (List[Tuple[int]]): The position of the snake and its tail in the grid as a list of (x, y) integer tuples. The last element in the list is the snake's head 
food (Tuple[int]): The position of the food in the grid as (x, y) tuple
prev_snake (List[Tuple[int]]): The position of the snake at the previous time step, in the same format as the snake argument
prev_food (Tuple[int]): The position of the food at the previous time step, in the smae format as the food argument
grid_size (Tuple[int]): The size of the grid where the snake is as a tuple of integers
is_done (bool): Only in the reward function, whether after the last action the game terminated
```

## The RL agent

The implemented default agent is a Deep Q learning agent, built as a 3 layer feedforward neural network, using the [Tensorflow Agents library](https://www.tensorflow.org/agents). It was made following the Deep Q network tutorial (that you can find [here](https://www.tensorflow.org/agents/tutorials/1_dqn_tutorial)) originally applied to the cartpole environment. It samples interactions with the environment, by playing the game, and then it uses those interactions to learn a Q function, i.e. the estimated discounted sum of future rewards conditioned on the current action.

At every timestep during training it receives the observation (by default an array of values), and it returns the Q value for each of the possible actions that it can take. Then, to balance exploration with exploitation, with random chance it either chooses a random action, or it chooses the action with the highest Q value. During testing and evaluation, the agent always chooses the best action. The probability with which a random action is chosen during training decreases as the training goes on.

If you do change the agent code, you will also need to update the `user_eval_fn.py` script, and get the `init` function to load the model from a specific folder, and the `agent_predict(...)` function to take an observation as input and return an action (as an integer) as output


## The Challenge and submission process

Your goal is to change code in either the agent, the training procedure, the observation function, the reward function or any combination of them, to train an agent to maximize the number of apples eaten during a game and how reliably it can do so. Solutions that take a lot of time to select actions will also be penalised (compute resources are not free), and **any solution that performs well in the end but does not actually use RL will be disqualified**. There is a limit over how much time the agent has to take to play 100 games, if it goes beyond, the evaluation is terminated and the submission is ignored.

In order to submit your solution you can run the `make_submission.py` script, providing your team name as argument. This will automatically zip the files that will be part of your submission and it will send them to a cloud storage bucket, from which the evaluation will be carried out. Keep in mind that it might take sometime for the evaluation to run through (especially if there are many people submitting at the same time). Once the submission has been evaluated, if the score is higher than your team's previous highest score, the leaderboard will be updated accordingly, otherwise nothing will happen. We recommend you extensively test your code before submitting it to ensure no errors can happen, but in case you want to check the logs from your submission, consider using the `check_submission_logs.py` script (refer to the Usage section).

For your submission to be valid, all of the python files with names starting with `user_` should be present (but not necessarily all of them updated), and there should be a folder named `model/` from which the submission agent can be loaded (through the `user_eval_fn.py` functions). The code should also work with the given python dependencies in `requirements.txt`, no more dependencies shall be used.

### Limits

In order to prevent excessive submissions and waste of compute resources we have put some limits in place for the submissions that you should consider while developing your solution. There is a rate limit on the number of submission each team can make over a certain period of time (please speak with the Hackathon's organizers for exact numbers). There is also a time limit on how long your agent should take to run the `evaluate_agent.py` script, also please speak with the organizers for the details.
