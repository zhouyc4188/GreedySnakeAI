from snake.algorithm import DQN
from snake.snake import Game
from snake.window import Window

base_size = 20
expansion = 1.5
number = 5
g = Game(number=number)
#window = Window(number=number, block_size=base_size, expansion=expansion, speed=0.2)
dqn = DQN(game=g)
dqn.train(None)
